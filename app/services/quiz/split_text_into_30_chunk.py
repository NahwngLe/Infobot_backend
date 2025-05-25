def split_30_chunk(texts):
    content = ""
    for text in texts:
        content += text

    length = len(content)
    print("Length of text: ", length)
    text_length = int(length/30)
    arr = []

    for i in range(0, 30):
        arr.append(content[i*text_length:i*text_length+text_length])
    return arr

split_30_chunk("The Infobot_backend is a FastAPI-based backend application designed to process PDF files, generate quizzes based on their content, and store both the PDFs and quizzes in a structured manner using MongoDB. It leverages Pinecone for efficient similarity searches on document embeddings. The backend exposes a set of REST API endpoints for managing PDFs and quizzes, enabling seamless integration with frontend applications. Prometheus and Alertmanager are integrated for monitoring and alerting. ")