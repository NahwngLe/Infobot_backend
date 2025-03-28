import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

PINECONE_ENVIRONMENT = "us-east-1"
INDEX_NAME = "langchainvectors"

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)
index.delete(delete_all=True, namespace="default")