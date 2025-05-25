import gridfs
from pinecone import Pinecone
from pymongo.mongo_client import MongoClient
from .config import *


pc = Pinecone(api_key=PINECONE_API_KEY)

# MongoDb
client = MongoClient(uri)
db = client["Infobot"]
fs = gridfs.GridFS(db)



