PROMPT_TEMPLATE_CREATE_QUIZ_ENGLISH = """
You are an expert at creating True/False and Multiple Choice questions based strictly on the content of the provided text.
Your task is to prepare high-quality quiz questions that test understanding of the key concepts, facts, and theoretical principles described in the text. 

Important instructions:
- Carefully read the provided text and identify the most important keywords or key concepts in it.
- Generate quiz questions that focus on these keywords or key concepts.
- Avoid creating questions that are vague, overly broad, or about content not explicitly mentioned.
- Do NOT create questions with options like "Which of the following is NOT mentioned" or "Which approach is not discussed".

For each text chunk below, create:
- True/False questions:
    + Each question must focus on a specific keyword or key concept identified in the text.
    + Keep the question concise and directly answerable from the text.
- Multiple Choice questions:
    + Each question should be based on an important keyword or concept from the text.
    + Provide 4 answer choices, with one correct answer.
    + Distractors should be plausible but incorrect.

Format the output as a JSON object, following this structure:
1. For True/False questions:
    - "question": The question text.
    - "options": ["True", "False"].
    - "answer": The index number (0 for "True", 1 for "False") of the correct answer.
    - "explanation": A brief explanation justifying the correct answer.

2. For Multiple Choice questions:
    - "question": The question text.
    - "options": An array of 4 possible answers.
    - "answer": The index number (0-3) of the correct answer.
    - "explanation": A brief explanation of the correct answer.

Example of a multiple choice question:
  "question": "What does the 'state space' represent in the context of Sokoban?",
  "options": [
      "The physical size of the game board.",
      "The number of boxes in the game.",
      "The set of all possible configurations of the game.",
      "The set of all possible moves the player can make."
  ],
  "answer": 2,
  "explanation": "The state space refers to all possible states that can occur in the game."

Ensure that all questions are derived directly from the provided text content.

Based on the following passage:
-----------
{text}
-----------

QUESTIONS:
"""


PROMPT_TEMPLATE_CREATE_QUIZ_VIETNAMESE = """
Bạn là một chuyên gia trong việc tạo câu hỏi Đúng/Sai và Trắc nghiệm Dựa trên nội dung của văn bản được cung cấp.
Nhiệm vụ của bạn là chuẩn bị các câu hỏi kiểm tra chất lượng cao, đánh giá mức độ hiểu biết về các khái niệm, dữ kiện và nguyên lý lý thuyết được mô tả trong văn bản.

Hướng dẫn quan trọng:
- Đọc kỹ đoạn văn và xác định những từ khóa hoặc khái niệm quan trọng nhất.
- Tạo câu hỏi tập trung chính vào các từ khóa, khái niệm đó.
- Tránh tạo các câu hỏi quá chung chung hoặc mơ hồ.
- KHÔNG tạo các câu hỏi dạng “Phương án nào sau đây KHÔNG được đề cập...” hay “Hướng tiếp cận nào không xuất hiện...” để đảm bảo câu hỏi đánh giá trực tiếp nội dung.
- Không tạo câu hỏi liên quan đến tiêu đề phần, đánh số hay tham khảo bên ngoài.
- Tránh các thông tin kiểu “như đã đề cập ở phần...” hoặc “văn bản nói về...”
- Tạo ít nhất 5 câu hỏi cho mỗi đoạn văn.
- Người làm bài không nhìn thấy đoạn văn gốc, nên câu hỏi phải rõ ràng và có thể trả lời dựa trên câu hỏi.

Với mỗi đoạn văn dưới đây, hãy tạo:
- Câu hỏi Đúng/Sai:
    + Mỗi câu hỏi tập trung vào một từ khóa hoặc khái niệm quan trọng trong văn bản.
    + Câu hỏi ngắn gọn, dễ trả lời dựa trên văn bản.
- Câu hỏi Trắc nghiệm:
    + Mỗi câu hỏi dựa trên một từ khóa hoặc khái niệm quan trọng.
    + Có 4 lựa chọn, chỉ 1 đáp án đúng.
    + Các lựa chọn sai phải hợp lý, nhưng không đúng.

Định dạng đầu ra dưới dạng JSON, theo cấu trúc sau:
1. Đối với câu hỏi Đúng/Sai:
    - "question": Văn bản câu hỏi.
    - "options": ["Đúng", "Sai"].
    - "answer": Số thứ tự đáp án đúng (0 cho "Đúng", 1 cho "Sai").
    - "explanation": Giải thích ngắn gọn lý do tại sao đáp án đúng.

2. Đối với câu hỏi Trắc nghiệm:
    - "question": Văn bản câu hỏi.
    - "options": Mảng gồm 4 lựa chọn đáp án.
    - "answer": Số thứ tự đáp án đúng (0-3).
    - "explanation": Giải thích ngắn gọn cho đáp án đúng.

Ví dụ câu hỏi trắc nghiệm:
  "question": "Trạng thái không gian trong Sokoban đề cập đến điều gì?",
  "options": [
      "Kích thước vật lý của bàn cờ.",
      "Số lượng hộp trong trò chơi.",
      "Tập hợp tất cả các cấu hình có thể của trò chơi.",
      "Tập hợp tất cả các nước đi có thể của người chơi."
  ],
  "answer": 2,
  "explanation": "Trạng thái không gian là tập hợp tất cả các trạng thái có thể xảy ra trong trò chơi."

Đảm bảo tất cả câu hỏi đều được tạo trực tiếp từ nội dung của văn bản.

Dựa trên đoạn văn sau:
-----------
{text}
-----------

CÂU HỎI:
"""
