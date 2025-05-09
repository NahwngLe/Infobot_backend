import os
from dotenv import load_dotenv

# API KEY
load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# HuggingFace token
HF_TOKEN = os.getenv("HF_TOKEN")
os.environ["HF_TOKEN"] = HF_TOKEN

# Pinecone
PINECONE_ENVIRONMENT = "us-east-1"
INDEX_NAME = "langchainvectors"

# MongoDb
uri = "mongodb+srv://nhanlequy12:nhanhero09@nhancluster.rfxde.mongodb.net/your_database?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"



