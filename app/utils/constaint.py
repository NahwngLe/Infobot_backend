PROMPT_TEMPLATE_CREATE_QUIZ_ENGLISH = """
    You are an expert at creating True/False and Multiple Choice questions based on documentation.
    Your goal is to prepare students for their test.

    For each text chunk below, create the following:
    
    - **True/False questions**: + Each question must be based on key facts or concepts from the text.
                                + The question should be concise and easy to answer.
    - **Multiple Choice questions**: + Each question must have four options, one of which is correct. 
                                     + The questions should assess comprehension of important details from the text.
    
    Format the output like this guide (The answer must be returned in JSON format):
    1. For True/False questions:
        - "question": The question,
        - "options": ["True", "False"],
        - "answer": The index number (0 or 1) of the correct answer in the options array.
        - "explanation" : The explanation to the answer
       
    2. For Multiple Choice questions:
        - "question": The question,
        - "options": An array of 4 strings representing the choices,
        - "answer": The index number (0-3) of the correct answer in the options array.
        - "explanation" : The explanation to the answer
    
    Example:
    
    "question": "What does the 'state space' represent in the context of Sokoban?",
    "options": [
        "The physical size of the game board.",
        "The number of boxes in the game.",
        "The set of all possible configurations of the game.",
        "The set of all possible moves the player can make."
    ],
    "answer": 2,
    "explanation": "The state space as the set of all possible states that can occur in the game."
    
    Ensure the questions are relevant to the content and concise.
    
    Based on the following passage:
    -----------
    {text}
    -----------
    
    QUESTIONS:
"""


PROMPT_TEMPLATE_CREATE_QUIZ_VIETNAMESE = """
    Bạn là chuyên gia trong việc tạo câu hỏi Đúng/Sai và Trắc nghiệm dựa trên tài liệu.
    Mục tiêu của bạn là giúp học sinh ôn tập cho bài kiểm tra.

    Với mỗi đoạn văn bản dưới đây, hãy tạo các nội dung sau:

    - **Câu hỏi Đúng/Sai**: + Mỗi câu hỏi phải dựa trên những sự thật hoặc khái niệm chính trong văn bản.
                            + Câu hỏi cần ngắn gọn và dễ trả lời.
    - **Câu hỏi Trắc nghiệm**: + Mỗi câu hỏi phải có bốn lựa chọn, trong đó chỉ có một đáp án đúng.
                               + Câu hỏi cần đánh giá mức độ hiểu nội dung quan trọng của đoạn văn.

    Định dạng kết quả theo hướng dẫn sau (Câu trả lời phải được trả về dưới dạng JSON):
    1. Đối với câu hỏi Đúng/Sai:
        - "question": Câu hỏi,
        - "options": ["Đúng", "Sai"],
        - "answer": Số thứ tự (0 hoặc 1) của đáp án đúng trong mảng options.
        - "explanation" : Giải thích cho đáp án.

    2. Đối với câu hỏi Trắc nghiệm:
        - "question": Câu hỏi,
        - "options": Mảng gồm 4 chuỗi là các lựa chọn,
        - "answer": Số thứ tự (0-3) của đáp án đúng trong mảng options.
        - "explanation" : Giải thích cho đáp án.

    Ví dụ:

    "question": "Không gian trạng thái là gì trong trò chơi Sokoban?",
    "options": [
        "Kích thước vật lý của bàn chơi.",
        "Số lượng hộp trong trò chơi.",
        "Tập hợp tất cả các cấu hình có thể có của trò chơi.",
        "Tập hợp tất cả các nước đi mà người chơi có thể thực hiện."
    ],
    "answer": 2,
    "explanation": "Không gian trạng thái là tập hợp tất cả các trạng thái có thể xảy ra trong trò chơi."

    Hãy đảm bảo các câu hỏi phù hợp với nội dung và ngắn gọn.

    Dựa trên đoạn văn sau:
    -----------
    {text}
    -----------

    CÂU HỎI:
"""
