import math
import re
import json
import time

from fastapi import HTTPException

from langchain_core.prompts import PromptTemplate

from app.utils.constaint import *

from app.database import *

def generate_quiz(pdf_id, user='default', language_of_quiz='eng'):
    start = time.time()

    batch_size = 10  # Number of pages per quiz creation
    query = {"pdf_id": pdf_id}
    result = db.users_pdf_files.find_one(query)
    if not result:
        raise HTTPException(status_code=404, detail="No document found with this pdf_id")

    # Take total_pages
    total_pages = result.get("total_pages", 0)
    max_page = math.ceil(total_pages / batch_size)
    for page in range(1, max_page+2):
        # Calculate pages that user need
        start_page = min((page - 1) * batch_size + 1, total_pages)
        if start_page > total_pages:
            continue  # Skip if total pages exceeded
        end_page = min(start_page + batch_size - 1, total_pages)
        # Get text paragraphs within page range
        result_list_documents = list(
            db.documents.find(
                {
                    "pdf_id": pdf_id,
                    "page": {"$gte": start_page, "$lte": end_page}
                }
            ).sort([("page", 1), ("subpage", 1)])
        )
        if not result_list_documents:
            # raise HTTPException(status_code=404, detail=f"No content found for page batch {page}.")
            return

        # Convert into chunks
        pdf_name = result["pdf_name"]
        pdf_name_hash = result["pdf_name_hash"]
        chunks = [document["text"] for document in result_list_documents]

        # Find duplicate quiz names and add numbers
        existing_quizzes = list(db.quiz.find({"metadata.pdf_id": pdf_id}, {"metadata.quiz_name": 1}))
        existing_quiz_names = [q["metadata"]["quiz_name"] for q in existing_quizzes]
        base_quiz_name = f"{pdf_name}_lang({language_of_quiz})_page({start_page}-{end_page})"
        quiz_name = base_quiz_name
        count = 1
        while quiz_name in existing_quiz_names:
            quiz_name = f"{base_quiz_name} ({count})"
            count += 1

        # Create quiz_list if it doesn't exist
        quiz_list = result.get("quiz_list", {})

        quiz_name = str(quiz_name)
        quiz_list[quiz_name] = quiz_name

        metadata_info = {
            "user": user,
            "quiz_name": quiz_name,
            "pdf_name": pdf_name,
            "page": page,
            "pdf_id": pdf_id,
            "pdf_name_hash": pdf_name_hash,
            "language": language_of_quiz
        }

        quizs = []
        quiz_to_db = []

        # Select prompt by language
        if language_of_quiz.lower() == 'vn':
            selected_prompt = PROMPT_TEMPLATE_CREATE_QUIZ_VIETNAMESE
        else:
            selected_prompt = PROMPT_TEMPLATE_CREATE_QUIZ_ENGLISH

        question_prompt = PromptTemplate(
            template=selected_prompt,
            input_variables=["text"]
        )

        # Create quiz
        for chunk in chunks:
            prompt = question_prompt.format(text=chunk)
            response = model.generate_content(prompt)

            try:
                raw_text = response.candidates[0].content.parts[0].text
                json_text = raw_text.strip("```json").strip("```")
                json_text = re.sub(r"\n", " ", json_text)
                quiz_data = json.loads(json_text)

                if isinstance(quiz_data, dict):
                    quiz_data = [quiz_data]

                quizs.append(quiz_data)
                time.sleep(1)

            except json.JSONDecodeError:
                print("Error decoding JSON response:", response)
                continue

        for quiz_question in quizs:
            for quiz in quiz_question:
                if isinstance(quiz, dict):
                    quiz["metadata"] = metadata_info
                    quiz_to_db.append(quiz)
                else:
                    print("Invalid quiz format:", quiz)

        end = time.time()
        print(f"Create quiz take {end - start} second ")

        # Insert quiz to mongoDB
        db.quiz.insert_many(quiz_to_db)
        # Updated quiz_list in users_pdf_files
        db.users_pdf_files.update_one(
            {"pdf_id": pdf_id},
            {"$set": {"quiz_list": quiz_list}}
        )

        yield {
            "message": "Create quiz success!!",
            "quiz_name": quiz_name,
            "page_of_pdf": f"{start_page}-{end_page}",
            "pdf_id": pdf_id,
            "pdf_name_hash": pdf_name_hash,
            "time_for_create_quiz": f"{end - start} second",
        }
