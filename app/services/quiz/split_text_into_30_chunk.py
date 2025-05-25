import math

def split_custom_chunk(texts, batch_size=15):
    if isinstance(texts, str):
        texts = [texts]

    content = "".join(texts)
    length = len(content)
    print("Length of text:", length)

    if length == 0:
        return []
    chunk_size = math.ceil(length / batch_size)
    arr = []

    for i in range(0, length, chunk_size):
        arr.append(content[i:i + chunk_size])

    return arr


# text = "The Infobot_backend is a FastAPI-based backend application designed to process PDF files, generate quizzes based on their content, and store both the PDFs and quizzes in a structured manner using MongoDB. It leverages Pinecone for efficient similarity searches on document embeddings. The backend exposes a set of REST API endpoints for managing PDFs and quizzes, enabling seamless integration with frontend applications. Prometheus and Alertmanager are integrated for monitoring and alerting."
# result = split_30_chunk(text)
# print(len(result))  # Kết quả: 30
# for i, chunk in enumerate(result):
#     print(f"Chunk {i+1}: {chunk}\n")