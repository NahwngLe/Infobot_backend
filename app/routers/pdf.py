from fastapi import APIRouter, UploadFile, File, HTTPException, Response
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_bytes
import io
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import gridfs
from bson import ObjectId
import hashlib
from app.utils.handlePdf import pdfBytesToText

uri = "mongodb+srv://nhanlequy12:nhanhero09@nhancluster.rfxde.mongodb.net/your_database?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
# Create a new client and connect to the server
client = MongoClient(uri)
# , server_api=ServerApi('1')
db = client["Infobot"]
fs = gridfs.GridFS(db)

router = APIRouter(prefix="/pdf", tags=["PDF"])
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@router.post("/upload")
async def upload_pdf (file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be pdf")
    
    try:
        pdf_bytes = await file.read()
        file_hash = hashlib.md5(pdf_bytes).hexdigest()
        
        #Kiểm tra file có tồn tại chưa
        existing_file = db.pdf_hash.find_one({"file_hash" : file_hash})
        if existing_file:
            return {
                "message": "File already exists",
                "filename": existing_file["filename"],
                "pdf_id": str(existing_file["pdf_id"]),
                "content": existing_file["content"],    
            }
            
        pdf_id = fs.put(pdf_bytes, filename=file.filename)
        
        texts, lang = pdfBytesToText(pdf_bytes)

        db.pdf_hash.insert_one({
            "filename": file.filename,
            "file_hash": file_hash,
            "pdf_id" : pdf_id,
            "content": texts,
        })
        
        return {
            "message": "Add file success",
            "filename": file.filename,
            "content": texts,
            "language": lang,
            "pdf_id": str(pdf_id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-pdf/{pdf_id}")
async def get_pdf(pdf_id: str):
    try:
        file = fs.get(ObjectId(pdf_id))
        return Response(content=file.read(), media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")
