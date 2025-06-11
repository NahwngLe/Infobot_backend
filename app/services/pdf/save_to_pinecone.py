from app.database import *
from pinecone import ServerlessSpec
from more_itertools import chunked

def save_to_pinecone(pdf_name, pdf_name_hash, INDEX_NAME, vectors, metadata, chunks, namespace='default'):
    # 1. Create Pinecone index if not exists
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

    index = pc.Index(INDEX_NAME)
    vector_pinecone = []

    # 2. Upsert metadata into each vectors
    for i, d in enumerate(chunks):
        meta = {
            "user_id": namespace,
            "pdf_name": pdf_name,
            "pdf_name_hash": pdf_name_hash,
            "source": d.metadata.get("source"),
            "page": d.metadata.get("page"),
            "subpage": d.metadata.get("subpage"),
            "total_pages": d.metadata.get("total_pages"),
            "text": d.page_content,
        }

        vector_pinecone.append({
            "id": f"{pdf_name_hash}_{i}",
            "values": vectors[i],
            "metadata": meta
        })

        if not vectors[i] or len(vectors[i]) != 1024:
            print("Invalid vector at", i)

    # 3. Upsert vectors to Pinecone (in batches)
    for batch in chunked(vector_pinecone, 100):
        index.upsert(vectors=batch, namespace=namespace)

    return len(vector_pinecone)