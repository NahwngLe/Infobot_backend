from fastapi import APIRouter, UploadFile, File, HTTPException, Response
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_bytes
import io
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import shutil
import gridfs
from bson import ObjectId
import hashlib
from app.utils.handlePdf import pdfBytesToText
from app.utils.flow_from_pdf_to_quiz import *

#MongoDb
uri = "mongodb+srv://nhanlequy12:nhanhero09@nhancluster.rfxde.mongodb.net/your_database?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
client = MongoClient(uri)
db = client["Infobot"]
fs = gridfs.GridFS(db)

router = APIRouter(prefix="/pdf", tags=["PDF"])
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@router.post("/upload")
def upload_pdf_and_save(file: UploadFile = File(...)):
    if file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be pdf")

    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    message = save_to_db(file)

    return message

@router.get("/get-pdf/{pdf_id}")
async def get_pdf(pdf_id: str):
    try:
        file = fs.get(ObjectId(pdf_id))
        return Response(content=file.read(), media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")
