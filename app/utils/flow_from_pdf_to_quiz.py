import openai
import langchain
import pinecone
import os
import re
from dotenv import load_dotenv
import torch
import json
import time
import gridfs

from fastapi import HTTPException
from pathlib import Path
import hashlib
from pymongo.mongo_client import MongoClient
from pinecone import Pinecone, ServerlessSpec

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_google_genai import GoogleGenerativeAI
import google.generativeai as genai
from langchain_core.prompts import PromptTemplate

from app.utils.constaint import *

#API KEY
load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
os.environ["HF_TOKEN"] = HF_TOKEN

#Pinecone
PINECONE_ENVIRONMENT = "us-east-1"
INDEX_NAME = "langchainvectors"

pc = Pinecone(api_key=PINECONE_API_KEY)

#MongoDb
uri = "mongodb+srv://nhanlequy12:nhanhero09@nhancluster.rfxde.mongodb.net/your_database?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
client = MongoClient(uri)
db = client["Infobot"]
fs = gridfs.GridFS(db)

#Embedding model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)

#Generative AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")



def load_document(pdf):
    file_loader = PyPDFLoader(pdf)
    document = file_loader.load()

    return document

def split_documents_into_chunks(pdf, chunk_size=512, chunk_overlap=100):
    # Split data to chunks
    documents = load_document(pdf)
    text_spliter = RecursiveCharacterTextSplitter(
        separators=[
            "\n\n",
            "\n",
            " ",
            ".",
            ",",
            "\u200b",  # Zero-width space
            "\uff0c",  # Fullwidth comma
            "\u3001",  # Ideographic comma
            "\uff0e",  # Fullwidth full stop
            "\u3002",  # Ideographic full stop
            "",
        ],
        chunk_size= chunk_size,
        chunk_overlap=chunk_overlap
    )
    texts = text_spliter.split_documents(documents)

    # Add subpage to track down the paragraph in page
    subpage = 0
    page_init = -1
    for text in texts:
        if (text.metadata["page"] == page_init):
            subpage += 1
            text.metadata["subpage"] = subpage
        else:
            subpage = 0
            text.metadata["subpage"] = 0
            page_init += 1

    for text in texts:
        # Remove /n in text
        text.page_content = re.sub(r"\n", " ", text.page_content)

    # print(len(texts))
    # print(len(documents))
    # for doc in documents:
    #     print(doc.metadata)
    return texts

def embedding_text(pdf):
    chunks = split_documents_into_chunks(pdf)

    # Embedding queries
    vectors = [embeddings.embed_query(chunk.page_content) for chunk in chunks]
    metadata = [chunk.metadata for chunk in chunks]
    return vectors, metadata, chunks

async def save_to_db(pdf, prototypeFile, namespace = 'default', user='default'):
    vectors, metadata, chunks = embedding_text(pdf)
    pdf_name = Path(metadata[0]["source"]).stem + "_" + str(metadata[0]["total_pages"]) + "_" + str(user)

    await prototypeFile.seek(0)
    file_content = await prototypeFile.read()
    if not file_content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")


    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,
            metric="cosine"
        )

    pdf_hash = hashlib.sha256(pdf_name.encode()).hexdigest()

    existing_file = db.users_pdf_files.find_one({"pdf_name_hash": pdf_hash, "user_id": user})
    if existing_file:
        return {
            "message": "File already exists",
            "pdf_id": existing_file["pdf_id"],
            "pdf_name_hash": existing_file["pdf_name_hash"],
            "filename": existing_file["pdf_name"],
            "content": "",
        }

    index = pc.Index(INDEX_NAME)

    pdf_id = fs.put(file_content, filename=prototypeFile.filename)
    pdf_id = str(pdf_id)
    #Vector embedding
    vector_pinecone = []
    #user - pdf_hash link db
    users_pdf_files = []
    #Chunks db
    documents_mongo = []
    texts = ""

    for i, (d, e) in enumerate(zip(chunks, vectors)):
        selected_metadata = {
            "user_id": user,
            "pdf_name": pdf_name,
            "pdf_name_hash": pdf_hash,
            "source": d.metadata.get("source"),
            "page": d.metadata.get("page"),
            "subpage": d.metadata.get("subpage"),
            "total_pages": d.metadata.get("total_pages"),
        }
        #Phai toi uu hieu suat cho nay
        users_pdf_files.append({
            "user_id": user,
            "pdf_name": pdf_name,
            "pdf_id": pdf_id,
            "pdf_name_hash": pdf_hash,
            "quiz_list": {},
            "source": d.metadata.get("source"),
            "total_pages": d.metadata.get("total_pages"),
        })
        texts += " " + str(d.page_content)
        documents_mongo.append({
            "text": d.page_content,
            "pdf_id": pdf_id,
            "pdf_name": pdf_name,
            "source": d.metadata.get("source"),
            "page": d.metadata.get("page"),
            "subpage": d.metadata.get("subpage"),
            "total_pages": d.metadata.get("total_pages"),
        })

        vector_pinecone.append((
            str(i),
            e,
            {**selected_metadata, "text": d.page_content}  # Metadata phải là dictionary
        ))

    #Add to Pinecone
    index.upsert(
        vectors=vector_pinecone,
        namespace=namespace
    )

    # Add to MongoDb
    db.users_pdf_files.insert_one(users_pdf_files[0])
    db.documents.insert_many(documents_mongo)

    return {
        "message": "Save to Pinecone, MongoDB successfully",
        "pinecone_vectors": len(vector_pinecone),  # Số lượng vector lưu vào Pinecone
        "mongo_documents": len(documents_mongo),  # Số lượng đoạn văn bản lưu vào documents
        "pdf_id": pdf_id,
        "content": texts,
        "pdf_name_hash": pdf_hash,
        "filename": users_pdf_files[0]["pdf_name"],
    }

# message = save_to_db('app/assest/pdf/main.pdf')
# print(message)


def generate_quiz(pdf_id, user='default', language_of_quiz='eng'):
    start = time.time()

    query = {"pdf_id": pdf_id}
    result = db.users_pdf_files.find_one(query)
    if not result:
        raise HTTPException(status_code=404, detail="No document found with this pdf_id")

    pdf_name = result["pdf_name"]
    pdf_name_hash = result["pdf_name_hash"]

    query_take_document = {"pdf_id": pdf_id}
    result_list_documents = db.documents.find(query_take_document)
    result_list_documents = list(result_list_documents)
    chunks = [document["text"] for document in result_list_documents]

    existing_quizzes = list(db.quiz.find({"metadata.pdf_id": pdf_id}, {"metadata.quiz_name": 1}))
    existing_quiz_names = [q["metadata"]["quiz_name"] for q in existing_quizzes]

    base_quiz_name = pdf_name
    quiz_name = base_quiz_name + f"_lang({language_of_quiz})"
    count = 1
    while quiz_name in existing_quiz_names:
        quiz_name = f"{base_quiz_name} ({count})"
        count += 1

    # Tạo quiz_list nếu chưa có
    existing_quiz = db.users_pdf_files.find_one({"pdf_id": pdf_id})
    quiz_list = existing_quiz.get("quiz_list", {}) if existing_quiz else {}

    quiz_name = str(quiz_name)
    quiz_list[quiz_name] = quiz_name

    metadata_info = {
        "user": user,
        "quiz_name": quiz_name,
        "pdf_name": pdf_name,
        "pdf_id": pdf_id,
        "pdf_name_hash": pdf_name_hash,
        "language": language_of_quiz
    }

    quizs = []
    quiz_to_db = []

    # Chọn prompt theo ngôn ngữ
    if language_of_quiz.lower() == 'vn':
        selected_prompt = PROMPT_TEMPLATE_CREATE_QUIZ_VIETNAMESE
    else:
        selected_prompt = PROMPT_TEMPLATE_CREATE_QUIZ_ENGLISH

    question_prompt = PromptTemplate(
        template=selected_prompt,
        input_variables=["text"]
    )

    for chunk in chunks:
        prompt = question_prompt.format(text=chunk)
        response = model.generate_content(prompt)

        try:
            raw_text = response.candidates[0].content.parts[0].text
            json_text = raw_text.strip("```json").strip("```")
            json_text = re.sub(r"\n", " ", json_text)
            quiz_data = json.loads(json_text)

            if isinstance(quiz_data, dict):
                quiz_data = [quiz_data]

            quizs.append(quiz_data)
            time.sleep(1)

        except json.JSONDecodeError:
            print("Error decoding JSON response:", response)
            continue

    for quiz_question in quizs:
        for quiz in quiz_question:
            if isinstance(quiz, dict):
                quiz["metadata"] = metadata_info
                quiz_to_db.append(quiz)
            else:
                print("Invalid quiz format:", quiz)

    end = time.time()
    print(f"Create quiz take {end - start} second ")

    end_save = time.time()
    db.quiz.insert_many(quiz_to_db)

    db.users_pdf_files.update_one(
        {"pdf_id": pdf_id},
        {"$set": {"quiz_list": quiz_list}}
    )

    print(f"Save quiz to db success, take {end_save - end} second ")

    return {
        "message": "Create quiz success!!",
        "quiz_name": quiz_name,
        "pdf_id": pdf_id,
        "pdf_name_hash": pdf_name_hash,
    }

# quiz_questions = generate_quiz('app/assest/pdf/main.pdf')
# print(json.dumps(quiz_questions, indent=4, ensure_ascii=False))
# print(type(quiz_questions))

