from langchain_community.document_loaders import PyPDFLoader

# Load document for file to text
def load_document(pdf):
    file_loader = PyPDFLoader(pdf)
    document = file_loader.load()

    return document

