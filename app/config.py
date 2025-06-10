import os
from dotenv import load_dotenv
import google.generativeai as genai
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

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

# Generative AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# # Embedding model
# model_name = "sentence-transformers/all-mpnet-base-v2"
# # model_kwargs = {'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
# embeddings = HuggingFaceEmbeddings(model_name=model_name)
model_name = "BAAI/bge-large-en-v1.5"
model_kwargs = {'device': 'cuda'}
encode_kwargs = {'normalize_embeddings': True}
embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    # model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
    query_instruction="Represent this question for retrieval: "
)
