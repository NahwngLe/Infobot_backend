from .text_splitter import split_documents_into_chunks
from langchain_huggingface import HuggingFaceEmbeddings

# Embedding model
model_name = "sentence-transformers/all-mpnet-base-v2"
# model_kwargs = {'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
embeddings = HuggingFaceEmbeddings(model_name=model_name)

def embedding_text(pdf):
    chunks = split_documents_into_chunks(pdf)

    # Embedding queries
    vectors = [embeddings.embed_query(chunk.page_content) for chunk in chunks]
    metadata = [chunk.metadata for chunk in chunks]
    return vectors, metadata, chunks
