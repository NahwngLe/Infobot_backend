from fastapi import APIRouter, UploadFile, File, HTTPException, Response
from fastapi.responses import StreamingResponse

import shutil
import json
from bson import ObjectId

from app.utils import save_to_db, generate_quiz
from app.database import *


router = APIRouter(prefix="/pdf", tags=["PDF"])
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@router.post("/upload")
async def upload_pdf_and_save(file: UploadFile = File(...)) :
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be pdf")
    try:
        temp_file_path = f"app/assest/pdf/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        message = await save_to_db(temp_file_path, file)

        return message

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-all-pdf/{user}")
def get_all_pdf(user: str):
    try:
        query = {"user_id": user}
        results = db.users_pdfs.find(query)
        results = list(results)

        if not results:
            raise HTTPException(status_code=404, detail="No pdf found for that user id")

        pdf_ids = []

        for result in results:
            data = {
                "pdf_id": result["pdf_id"],
                "pdf_name": result["pdf_name"],
                "pdf_name_hash": result["pdf_name_hash"],
            }

            pdf_ids.append(data)
        return pdf_ids

    except Exception as e:
        raise HTTPException(status_code=501, detail=str(e))

@router.get("/get-pdf/{pdf_id}")
async def get_pdf(pdf_id: str):
    try:
        file = fs.get(ObjectId(pdf_id))
        if not file:
            raise HTTPException(status_code=404, detail="File not found, please enter valid pdf_id")
        return Response(content=file.read(), media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/create-quiz/{pdf_id}")
def create_quiz_from_pdf(
    pdf_id: str,
    language_of_quiz: str,
):
    def stream():
        try:
            for result in generate_quiz(pdf_id, language_of_quiz=language_of_quiz):
                yield json.dumps(result) + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(stream(), media_type="application/json")


@router.get("/get-quiz/{pdf_id}")
async def get_quiz(pdf_id: str):
    try:
        pipeline = [
            {
                "$match": {
                    "metadata.pdf_id": pdf_id
                }},
            {
                "$group": {
                    "_id": "$metadata.quiz_name",
                    "quizzes": {
                        "$push": {
                            "_id": "$_id",
                            "question": "$question",
                            "options": "$options",
                            "answer": "$answer",
                            "explanation": "$explanation",
                            "metadata": "$metadata"
                        }}}},
            {
                "$project": {
                    "_id": 0,
                    "quiz_name": "$_id",
                    "quizzes": 1
                }}
        ]
        result = list(db.quiz.aggregate(pipeline))

        if not result or result == {}:
            return
            # raise HTTPException(status_code=404, detail="No quizzes found for this pdf_name_hash")


        # convert ObjectId to str
        for group in result:
            for quiz in group["quizzes"]:
                quiz["_id"] = str(quiz["_id"])


        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal sever error: {str(e)}")