from app.database import *

async def save_pdf_to_mongo(pdf_name, prototypefile,
                            metadata, chunks,
                            pdf_name_hash, file_content,
                            user):

    # 1. Check if file already exists
    existing_file = db.users_pdfs.find_one({"pdf_name_hash": pdf_name_hash, "user_id": user})
    if existing_file:
        return {
            "message": "File already exists",
            "pdf_id": existing_file["pdf_id"],
            "pdf_name_hash": existing_file["pdf_name_hash"],
            "filename": existing_file["pdf_name"],
            "content": "",
        }

    # 2. Save file to GridFS
    pdf_id = fs.put(file_content, filename=prototypefile.filename)
    pdf_id = str(pdf_id)

    # 3. Prepare users_pdfs table data
    users_pdfs = {
        "user_id": user,
        "pdf_name": pdf_name,
        "pdf_id": pdf_id,
        "pdf_name_hash": pdf_name_hash,
        "quiz_list": {},
        "source": metadata[0].get("source"),
        "total_pages": metadata[0].get("total_pages"),
    }
    documents_mongo = []
    texts = ""

    # 4. Prepare documents tables data
    for i, d in enumerate(chunks):
        meta = {
            "user_id": user,
            "pdf_name": pdf_name,
            "pdf_name_hash": pdf_name_hash,
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

        texts += " " + d.page_content

    # 8. Save documents to MongoDB
    # users_pdfs is a linked table between documents and user
    db.users_pdfs.insert_one(users_pdfs)
    db.documents.insert_many(documents_mongo)

    # 9. Return response
    return {
        "message": "Saved to MongoDB successfully",
        "filename": pdf_name,
        "mongo_documents": len(documents_mongo),
        "pdf_id": pdf_id,
        "pdf_name_hash": pdf_name_hash,
        "content": texts,
    }
