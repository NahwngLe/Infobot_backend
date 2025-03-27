import openai
import langchain
import pinecone
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone

load_dotenv()

def load_document(pdf):
    file_loader = PyPDFLoader(pdf)
    document = file_loader.load()

    return document

documents = load_document('app/assest/pdf/main.pdf')
print(documents)

file = ""
print(file.read())