from pathlib import Path
import hashlib

from more_itertools import chunked
from fastapi import HTTPException

from app.services.pdf.chunks_embedding import *
from app.services.pdf.save_to_mongodb import save_pdf_to_mongo

from app.database import *

async def save_to_db(pdf, prototypefile, user_id='default'):
    try:
        # 1. Embedding pdf content
        print("Embedding pdf content")
        vectors, metadata, chunks = embedding_text(pdf)
        if not vectors or not metadata or not chunks:
            raise HTTPException(status_code=400, detail="Embedding failed or returned empty results")
        # Adding unique pdf name
        pdf_name = Path(metadata[0]["source"]).stem + "_" + str(metadata[0]["total_pages"])

        # 2. Read file content for GridFs
        print("Read file content for GridFs")
        await prototypefile.seek(0)
        file_content = await prototypefile.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        # 3. Hash pdf name for unique pdf
        print("Hash pdf name for unique pdf")
        pdf_name_hash = hashlib.sha256(pdf_name.encode()).hexdigest()

        message_from_mongodb = await save_pdf_to_mongo(pdf_name, prototypefile,
                                                    metadata, chunks,
                                                    pdf_name_hash, file_content,
                                                    user_id)
        return message_from_mongodb

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

