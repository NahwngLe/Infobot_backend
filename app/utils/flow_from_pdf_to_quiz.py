import openai
import langchain
import pinecone
import os
import re
from dotenv import load_dotenv
import torch
import json
import time

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

#Embedding model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)

#Generative AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

#PromptTemplate
question_prompt = PromptTemplate(
    template=PROMPT_TEMPLATE_CREATE_QUIZ,
    input_variables=["text"]
)


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

def save_to_db(pdf, namespace = 'default', user='default'):
    vectors, metadata, chunks = embedding_text(pdf)
    pdf_name = Path(metadata[0]["source"]).stem + "_" + str(metadata[0]["total_pages"]) + "_" + str(user)
    print(pdf_name)

    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,  # all-MiniLM-L6-v2 có vector kích thước 384
            metric="cosine"
        )

    pdf_hash = hashlib.sha256(pdf_name.encode()).hexdigest()

    existing_file = db.users_pdf_files.find_one({"pdf_name_hash": pdf_hash, "user": user})
    if existing_file:
        return {
            "message": "File already exists",
            # "filename": existing_file["filename"],
            # "pdf_id": str(existing_file["pdf_id"]),
            # "content": existing_file["content"],
        }

    index = pc.Index(INDEX_NAME)

    #Vector embedding
    vector_pinecone = []
    #user - pdf_hash link db
    users_pdf_files = []
    #Chunks db
    documents_mongo = []

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
        #Toi uu hieu suat
        users_pdf_files.append({
            "user_id": user,
            "pdf_name": pdf_name,
            "pdf_name_hash": pdf_hash,
            "source": d.metadata.get("source"),
            "total_pages": d.metadata.get("total_pages"),
        })

        documents_mongo.append({
            "text": d.page_content,
            "pdf_name": pdf_name,
            "pdf_name_hash": pdf_hash,
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
        "mongo_users_pdf_files": len(users_pdf_files),  # Số lượng tệp lưu vào users_pdf_files
        "mongo_documents": len(documents_mongo)  # Số lượng đoạn văn bản lưu vào documents
    }

# message = save_to_db('app/assest/pdf/main.pdf')
# print(message)


def generate_quiz(pdf, user='default'):
    start = time.time()
    chunks = split_documents_into_chunks(pdf)
    metadata = [chunk.metadata for chunk in chunks]
    pdf_name = Path(metadata[0]["source"]).stem + "_" + str(metadata[0]["total_pages"]) + "_" + str(user)
    quiz_name = pdf_name
    pdf_hash = hashlib.sha256(pdf_name.encode()).hexdigest()

    # # If existing then create a copy of quiz
    # existing_file = db.users_pdf_files.find_one({"pdf_name_hash": pdf_hash})
    # if existing_file:
    #     match = bool(re.search(r"\(\d+\)$", (Cai nay phai tim ben quiz)["metadata"]["quiz_name"]))
    #     if match:
    #         x = re.findall(r"(\d)", existing_file["metadata"]["quiz_name"])
    #         x_new = str(int(x[-1]) + 1) + ")"
    #         quiz_name = re.sub(r"(\d)\)$", x_new, existing_file["metadata"]["quiz_name"])
    #     else:
    #         quiz_name = existing_file["metadata"]["quiz_name"] + "(1)"

    quizs = []
    quiz_to_db = []

    for chunk in chunks:
        prompt = question_prompt.format(text=chunk.page_content)
        # response = llm.invoke(input=prompt)
        response = model.generate_content(prompt)

        try:
            raw_text = response.candidates[0].content.parts[0].text
            json_text = raw_text.strip("```json").strip("```")
            json_text = re.sub(r"\n", " ", json_text)
            quiz_data = json.loads(json_text)

            if isinstance(quiz_data, dict):
                quiz_data = [quiz_data]

            quizs.append(quiz_data)

        except json.JSONDecodeError:
            print("Error decoding JSON response:", response)
    # flat_list = [item for sublist in quiz_questions for item in sublist]
    # print(json.dumps(quiz_questions, indent=4, ensure_ascii=False))
    metadata_info = {
        "user": user,
        "quiz_name": quiz_name,
        "pdf_name": pdf_name,
        "pdf_hash": pdf_hash
    }
    i=0
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
    db.quiz_questions.insert_many(quiz_to_db)
    print(f"Save quiz to db success, take {end_save - end} second ")

    return quiz_to_db

# quiz_questions = generate_quiz('app/assest/pdf/main.pdf')
# print(json.dumps(quiz_questions, indent=4, ensure_ascii=False))
# print(type(quiz_questions))

