from app.utils import split_documents_into_chunks
from multiprocessing import Pool, cpu_count
from app.config import embeddings


def embedding_text(texts):
    chunks = texts
    chunk_contents = [chunk.page_content for chunk in chunks]

    vectors = embeddings.embed_documents(chunk_contents)
    metadata = [chunk.metadata for chunk in chunks]
    return vectors, metadata, chunks
