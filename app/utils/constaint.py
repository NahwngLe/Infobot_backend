PROMPT_TEMPLATE_CREATE_QUIZ = """
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
        - "explanation" : The explanation to the answer based on the text
       
    2. For Multiple Choice questions:
        - "question": The question,
        - "options": An array of 4 strings representing the choices,
        - "answer": The index number (0-3) of the correct answer in the options array.
        - "explanation" : The explanation to the answer based on the text
    
    Example:
    
    "question": "What does the 'state space' represent in the context of Sokoban?",
    "options": [
        "The physical size of the game board.",
        "The number of boxes in the game.",
        "The set of all possible configurations of the game.",
        "The set of all possible moves the player can make."
    ],
    "answer": 2,
    "explanation": "The text defines the state space as the set of all possible states that can occur in the game."
    
    Ensure the questions are relevant to the content and concise.
    
    Based on the following passage:
    -----------
    {text}
    -----------
    
    QUESTIONS:
"""