import openai
import langchain
import pinecone
import os
import re
from dotenv import load_dotenv
import torch
from pinecone import Pinecone, ServerlessSpec

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
os.environ["HF_TOKEN"] = HF_TOKEN

PINECONE_ENVIRONMENT = "us-east-1"
INDEX_NAME = "langchainvectors"

pc = Pinecone(api_key=PINECONE_API_KEY)
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

    print(len(texts))
    # print(len(documents))
    # for doc in documents:
    #     print(doc.metadata)
    return texts

def embedding_text(pdf):
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
    chunks = split_documents_into_chunks(pdf)
    # Initial embedding model
    embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)

    # Embedding queries
    vectors = [embeddings.embed_query(chunk.page_content) for chunk in chunks]
    metadata = [chunk.metadata for chunk in chunks]
    return vectors, metadata, chunks

def save_to_db(pdf, namespace = 'default'):
    vectors, metadata, chunks = embedding_text(pdf)

    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,  # all-MiniLM-L6-v2 có vector kích thước 384
            metric="cosine"
        )

    index = pc.Index(INDEX_NAME)
    vector_pinecone = []
    for i, (d, e) in enumerate(zip(chunks, vectors)):  # Thêm chỉ mục `i`
        selected_metadata = {
            "page": d.metadata.get("page"),
            "page_label": d.metadata.get("page_label"),
            "source": d.metadata.get("source"),
            "subpage": d.metadata.get("subpage"),
            "total_pages": d.metadata.get("total_pages")
        }

        vector_pinecone.append((
            str(i),
            e,
            {**selected_metadata, "text": d.page_content}  # Metadata phải là dictionary
        ))

    index.upsert(
        vectors=vector_pinecone,
        namespace=namespace
    )

    return {
        "message": "Save to Pinecone successfully",
    }

message = save_to_db('app/assest/pdf/main.pdf')
print(message)

def generate_quiz(pdf):
    chunks = split_documents_into_chunks(pdf)
    prompt = PromptTemplate.from_template("""
        Generate quiz questions based on the following text. The output must be in JSON format.
        Requirements:
            + Generate multiple-choice and Yes/No question only
            + Each question corresponding with multiple-choice should be 4 options
            + Clearly indicate the correct answer.
            + Provide a brief explanation for why the correct answer is correct.
            + The output format must be valid JSON.
    """)


generate_quiz('app/assest/pdf/main.pdf')