from app.database import *
from pinecone import ServerlessSpec

def save_pdf_embedding_to_pinecone(pdf_name, pdf_hash, INDEX_NAME, user, vectors, chunks, namespace='default'):
    # 1. Create Pinecone index if not exists
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

    index = pc.Index(INDEX_NAME)
    vector_pinecone = []

    # # 7. Upsert vectors to Pinecone (in batches)
    # for batch in chunked(vector_pinecone, 100):
    #     index.upsert(vectors=batch, namespace=namespace)
    return len(vector_pinecone)