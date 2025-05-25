from app.utils import split_documents_into_chunks
from langchain_huggingface import HuggingFaceEmbeddings
from multiprocessing import Pool, cpu_count

# Embedding model
model_name = "sentence-transformers/all-mpnet-base-v2"
# model_kwargs = {'device': 'cuda' if torch.cuda.is_available() else 'cpu'}
embeddings = HuggingFaceEmbeddings(model_name=model_name)

def embed_chunk(chunk_content):
    return embeddings.embed_query(chunk_content)
def embedding_text(pdf):
    chunks = split_documents_into_chunks(pdf)
    print("Xong chunks ", len(chunks))
    # Embedding queries
    with Pool(cpu_count()) as pool:
        vectors = pool.map(embed_chunk, [chunk.page_content for chunk in chunks])
    print("Xong multi ", len(vectors))
    metadata = [chunk.metadata for chunk in chunks]
    print("Xong metadata ", len(metadata))
    return vectors, metadata, chunks
