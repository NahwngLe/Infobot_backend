import math
import re
import json
import time
from multiprocessing import Pool, cpu_count

from fastapi import HTTPException
from langchain_core.prompts import PromptTemplate

from app.services.quiz.quiz_prompt import *
from app.database import *

def generate_quiz_for_chunk(args):
    chunk_content, metadata_info, selected_prompt = args

    # Nếu chunk quá ngắn hoặc chỉ là tiêu đề/lời mở đầu → bỏ qua
    skip_keywords = ['title', 'cover', 'table of contents', 'author', 'preface', 'introduction', 'copyright']
    if len(chunk_content.strip()) < 50 or any(kw.lower() in chunk_content.lower() for kw in skip_keywords):
        print("Skipping chunk (too short or irrelevant)")
        return []

    question_prompt = PromptTemplate(template=selected_prompt, input_variables=["text"])
    prompt = question_prompt.format(text=chunk_content)

    try:
        print("Đang tạo quiz")
        response = model.generate_content(prompt)
        raw_text = response.candidates[0].content.parts[0].text
        json_text = raw_text.strip("```json").strip("```")
        json_text = re.sub(r"\n", " ", json_text)
        quiz_data = json.loads(json_text)

        if isinstance(quiz_data, dict):
            quiz_data = [quiz_data]

        for quiz in quiz_data:
            quiz["metadata"] = metadata_info
        print("Tạo quiz thành công")
        return quiz_data

    except Exception as e:
        print(f"Error processing chunk: {e}")
        return []

def generate_quiz(pdf_id, user='default', language_of_quiz='eng'):
    start = time.time()
    # Find pdf if exist
    query = {"pdf_id": pdf_id}
    result = db.users_pdfs.find_one(query)
    if not result:
        raise HTTPException(status_code=404, detail="No document found with this pdf_id")

    # Take pdf name and hash
    pdf_name = result["pdf_name"]
    pdf_name_hash = result["pdf_name_hash"]

    # Take pdf text
    query_2 = {"pdf_id": result["pdf_id"]}
    result_2 = db.documents.find(query_2)
    chunks = [chunk["text"] for chunk in result_2]

    # Find duplicate quiz names and add numbers
    existing_quizzes = list(db.quiz.find({"metadata.pdf_id": pdf_id}, {"metadata.quiz_name": 1}))
    existing_quiz_names = [q["metadata"]["quiz_name"] for q in existing_quizzes]
    base_quiz_name = f"{pdf_name}_lang({language_of_quiz})"
    quiz_name = base_quiz_name
    count = 1
    while quiz_name in existing_quiz_names:
        quiz_name = f"{base_quiz_name} ({count})"
        count += 1

    # Adding quiz to quiz_list
    quiz_list = result.get("quiz_list", {})
    quiz_list[quiz_name] = quiz_name

    metadata_info = {
        "user": user,
        "quiz_name": quiz_name,
        "pdf_name": pdf_name,
        "pdf_id": pdf_id,
        "pdf_name_hash": pdf_name_hash,
        "language": language_of_quiz
    }
    selected_prompt = PROMPT_TEMPLATE_CREATE_QUIZ_VIETNAMESE \
                    if language_of_quiz.lower() == 'vn' \
                    else PROMPT_TEMPLATE_CREATE_QUIZ_ENGLISH

    # Chuẩn bị dữ liệu cho multiprocessing
    chunk_args = [(chunk, metadata_info, selected_prompt) for chunk in chunks]

    # Multiprocessing
    with Pool(cpu_count()) as pool:
        results = pool.map(generate_quiz_for_chunk, chunk_args)

    # Collect quizzes
    quiz_to_db = []
    for quiz_list_chunk in results:
        quiz_to_db.extend(quiz_list_chunk)
    end = time.time()
    print(f"Create quiz take {end - start} second ")

    # Add quiz to mongodb
    if quiz_to_db:
        db.quiz.insert_many(quiz_to_db)
    else:
        print("No quiz generated.")

    # Updated quiz_list in users_pdfs document
    db.users_pdfs.update_one(
        {"pdf_id": pdf_id},
        {"$set": {"quiz_list": quiz_list}}
    )

    return {
        "message": "Create quiz success!!" if quiz_to_db else "No quiz generated.",
        "quiz_name": quiz_name,
        "pdf_id": pdf_id,
        "pdf_name_hash": pdf_name_hash,
        "time_for_create_quiz": f"{end - start} second",
    }