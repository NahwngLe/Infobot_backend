import os

from fastapi import APIRouter, UploadFile, File, HTTPException, Response, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from bson import ObjectId
import shutil

# from app.routers.auth import oauth2_bearer
from app.services.quiz.generator import generate_quiz
from app.services.pdf.storage import save_to_db
from app.database import db, fs

import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")
def get_current_user_id(token: str = Depends(oauth2_bearer)):
    try:
        print("Sao payload không chạy dcmdcm")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Sao user_id không chạy dcmdcm")
        user_id: str = payload.get("user_id")
        print("user_id", user_id)
        if user_id is None:
            print("Neu khong cos user id thi chay dong nay")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user_id
    except JWTError:
        print("JWTError")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


router = APIRouter(prefix="/pdf", tags=["PDF"])


@router.post("/upload")
async def upload_pdf_and_save(file: UploadFile = File(...), user_id: str = Depends(get_current_user_id)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be pdf")
    try:
        temp_file_path = f"app/assest/pdf/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        message = await save_to_db(temp_file_path, file, user_id=user_id)
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-all-pdf")
def get_all_pdf(user_id: str = Depends(get_current_user_id)):
    try:
        query = {"user_id": user_id}
        results = list(db.users_pdfs.find(query))

        if results == []:
            results = None

        if not results:
            raise HTTPException(status_code=404, detail="No pdf found for this user")

        pdf_ids = [
            {
                "pdf_id": str(result["pdf_id"]),
                "pdf_name": result["pdf_name"],
                "pdf_name_hash": result["pdf_name_hash"]
            }
            for result in results
        ]
        return pdf_ids
    except Exception as e:
        raise HTTPException(status_code=501, detail=str(e))


@router.get("/get-pdf/{pdf_id}")
async def get_pdf(pdf_id: str, user_id: str = Depends(get_current_user_id)):
    try:
        file = fs.get(ObjectId(pdf_id))
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        metadata = db.users_pdfs.find_one({"pdf_id": pdf_id, "user_id": user_id})
        if not metadata:
            raise HTTPException(status_code=403, detail="Not authorized to access this file")
        return Response(content=file.read(), media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/create-quiz/{pdf_id}")
def create_quiz_from_pdf(pdf_id: str, language_of_quiz: str, user_id: str = Depends(get_current_user_id)):
    try:
        print("Find pdf")
        metadata = db.users_pdfs.find_one({"pdf_id": pdf_id, "user_id": user_id})
        if not metadata:
            raise HTTPException(status_code=403, detail="Not authorized to access this file")
        print("Chạy hàm tạo quiz")
        result = generate_quiz(pdf_id, language_of_quiz=language_of_quiz, user_id=user_id)
        print("Trả response")
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/get-quiz/{pdf_id}")
async def get_quiz(pdf_id: str, user_id: str = Depends(get_current_user_id)):
    try:
        metadata = db.users_pdfs.find_one({"pdf_id": pdf_id, "user_id": user_id})
        if not metadata:
            raise HTTPException(status_code=403, detail="Not authorized to access this quiz")

        pipeline = [
            {"$match": {"metadata.pdf_id": pdf_id, "metadata.user_id": user_id}},
            {"$group": {
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
            {"$project": {"_id": 0, "quiz_name": "$_id", "quizzes": 1}}
        ]
        result = list(db.quiz.aggregate(pipeline))

        if not result:
            raise HTTPException(status_code=404, detail="No quizzes found")

        # Convert ObjectId
        for group in result:
            for quiz in group["quizzes"]:
                quiz["_id"] = str(quiz["_id"])

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
