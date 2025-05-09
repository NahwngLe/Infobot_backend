import gridfs
from pinecone import Pinecone
import google.generativeai as genai
from pymongo.mongo_client import MongoClient
from .config import *


pc = Pinecone(api_key=PINECONE_API_KEY)

# MongoDb
client = MongoClient(uri)
db = client["Infobot"]
fs = gridfs.GridFS(db)

# Generative AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

