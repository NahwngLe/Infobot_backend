PROMPT_TEMPLATE_CREATE_QUIZ = """
    You are an expert at creating True/False and Multiple Choice questions based on documentation.
    Your goal is to prepare students for their test.
    
    Requirements:
        + Generate multiple-choice and Yes/No question only
        + Each question corresponding with multiple-choice should be 4 options
        + Clearly indicate the correct answer.
        + Provide a brief explanation for why the correct answer is correct.
        + The output format must be valid JSON.

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
       
    2. For Multiple Choice questions:
        - "question": The question,
        - "options": An array of 4 strings representing the choices,
        - "answer": The index number (0-3) of the correct answer in the options array.
    
    Ensure the questions are relevant to the content and concise.
    
    Based on the following passage:
    -----------
    {text}
    -----------
    
    QUESTIONS:
"""