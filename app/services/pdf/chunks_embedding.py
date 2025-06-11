from app.utils import split_documents_into_chunks
from multiprocessing import Pool, cpu_count
from app.config import embeddings
import time


def embedding_text(pdf):
    chunks = split_documents_into_chunks(pdf)
    start = time.time()
    chunk_contents = [chunk.page_content for chunk in chunks]

    vectors = embeddings.embed_documents(chunk_contents)
    metadata = [chunk.metadata for chunk in chunks]
    end = time.time()
    print("Time embedding (s): ", end-start)
    print("Number of vector embedding: ", len(vectors))
    return vectors, metadata, chunks
