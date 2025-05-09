from pathlib import Path
import hashlib
from pinecone import Pinecone, ServerlessSpec

from more_itertools import chunked
from fastapi import HTTPException

from .embedding_service import *

from app.database import *

async def save_to_db(pdf, prototypeFile, namespace='default', user='default'):
    try:
        # 1. Embedding
        vectors, metadata, chunks = embedding_text(pdf)
        if not vectors or not metadata or not chunks:
            raise HTTPException(status_code=400, detail="Embedding failed or returned empty results")

        pdf_name = Path(metadata[0]["source"]).stem + "_" + str(metadata[0]["total_pages"]) + "_" + str(user)

        # 2. Read file content
        await prototypeFile.seek(0)
        file_content = await prototypeFile.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        # 3. Create Pinecone index if not exists
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

        pdf_hash = hashlib.sha256(pdf_name.encode()).hexdigest()

        # 4. Check if file already exists
        existing_file = db.users_pdf_files.find_one({"pdf_name_hash": pdf_hash, "user_id": user})
        if existing_file:
            return {
                "message": "File already exists",
                "pdf_id": existing_file["pdf_id"],
                "pdf_name_hash": existing_file["pdf_name_hash"],
                "filename": existing_file["pdf_name"],
                "content": "",
            }

        # 5. Save file to GridFS
        pdf_id = fs.put(file_content, filename=prototypeFile.filename)
        pdf_id = str(pdf_id)

        # 6. Prepare data
        index = pc.Index(INDEX_NAME)
        vector_pinecone = []
        users_pdf_file = {
            "user_id": user,
            "pdf_name": pdf_name,
            "pdf_id": pdf_id,
            "pdf_name_hash": pdf_hash,
            "quiz_list": {},
            "source": metadata[0].get("source"),
            "total_pages": metadata[0].get("total_pages"),
        }
        documents_mongo = []
        texts = ""

        for i, (d, e) in enumerate(zip(chunks, vectors)):
            meta = {
                "user_id": user,
                "pdf_name": pdf_name,
                "pdf_name_hash": pdf_hash,
                "source": d.metadata.get("source"),
                "page": d.metadata.get("page"),
                "subpage": d.metadata.get("subpage"),
                "total_pages": d.metadata.get("total_pages"),
                "text": d.page_content,
            }

            documents_mongo.append({
                "text": d.page_content,
                "pdf_id": pdf_id,
                "pdf_name": pdf_name,
                "source": d.metadata.get("source"),
                "page": d.metadata.get("page"),
                "subpage": d.metadata.get("subpage"),
                "total_pages": d.metadata.get("total_pages"),
            })

            vector_pinecone.append((str(i), e, meta))
            texts += " " + d.page_content

        # 7. Upsert vectors to Pinecone (in batches)
        for batch in chunked(vector_pinecone, 100):
            index.upsert(vectors=batch, namespace=namespace)

        # 8. Save to MongoDB
        db.users_pdf_files.insert_one(users_pdf_file)
        db.documents.insert_many(documents_mongo)

        # 9. Return response
        return {
            "message": "Saved to Pinecone and MongoDB successfully",
            "pinecone_vectors": len(vector_pinecone),
            "mongo_documents": len(documents_mongo),
            "pdf_id": pdf_id,
            "content": texts,
            "pdf_name_hash": pdf_hash,
            "filename": pdf_name,
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

