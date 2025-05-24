# Infobot_backend

## Overview

The `Infobot_backend` is a FastAPI-based backend application designed to process PDF files, generate quizzes based on their content, and store both the PDFs and quizzes in a structured manner using MongoDB. It leverages Pinecone for efficient similarity searches on document embeddings.  The backend exposes a set of REST API endpoints for managing PDFs and quizzes, enabling seamless integration with frontend applications. Prometheus and Alertmanager are integrated for monitoring and alerting.

## Key Features

*   **PDF Upload and Processing:**  Handles PDF uploads, extracts text, and stores the PDF content in MongoDB GridFS.
*   **Quiz Generation:** Automatically generates quizzes (True/False and Multiple Choice) from PDF content using the Gemini AI model.
*   **Data Storage:** Utilizes MongoDB for storing PDF metadata, document chunks, and quizzes, and Pinecone for storing vector embeddings of PDF chunks.
*   **API Endpoints:** Provides RESTful API endpoints for uploading PDFs, retrieving PDFs, creating quizzes, and retrieving quizzes.
*   **Monitoring and Alerting:** Integrated with Prometheus and Alertmanager for real-time monitoring and alerting.

## Technologies Used

*   FastAPI
*   MongoDB
*   Pinecone
*   Langchain
*   Hugging Face Embeddings
*   Google Gemini AI
*   Prometheus
*   Alertmanager

## Getting Started

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd Infobot_backend
    ```

2.  **Set up environment variables:**

    *   Create a `.env` file in the root directory.
    *   Add the following environment variables:

        ```
        PINECONE_API_KEY=<your_pinecone_api_key>
        GEMINI_API_KEY=<your_gemini_api_key>
        HF_TOKEN=<your_huggingface_token>
        ```

3.  **Build and run the Docker containers:**

    ```bash
    docker-compose up --build
    ```

    This command builds the Docker image and starts the FastAPI application, Prometheus, and other necessary services.

4.  **Access the application:**

    *   FastAPI application: `http://localhost:8000`
    *   Prometheus: `http://localhost:9090`

## API Endpoints

| Endpoint                   | Method | Description                                    |
| -------------------------- | ------ | ---------------------------------------------- |
| `/pdf/upload`              | POST   | Upload a PDF file.                             |
| `/pdf/get-all-pdf/{user}` | GET    | Retrieve all PDFs for a specific user.         |
| `/pdf/get-pdf/{pdf_id}`    | GET    | Retrieve a specific PDF by its ID.             |
| `/pdf/create-quiz/{pdf_id}` | GET    | Create a quiz for a specific PDF.              |
| `/pdf/get-quiz/{pdf_id}`    | GET    | Retrieve quizzes for a specific PDF.           |

## Monitoring

Prometheus is configured to monitor the FastAPI application.  Alertmanager is used to send alerts based on predefined rules (e.g., instance downtime).  See [monitoring/prometheus.yml](https://github.com/NahwngLe/Infobot_backend/blob/main/monitoring/prometheus.yml) and [monitoring/alert.rules.yml](https://github.com/NahwngLe/Infobot_backend/blob/main/monitoring/alert.rules.yml) for configuration details.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant FastAPI
    participant MongoDB
    participant Pinecone
    participant GeminiAI

    User->>Frontend: Uploads PDF
    Frontend->>FastAPI: POST /pdf/upload
    FastAPI->>MongoDB: Saves PDF (GridFS)
    FastAPI->>FastAPI: Extracts Text Chunks
    FastAPI->>Pinecone: Creates Embeddings and Saves
    User->>Frontend: Request Quiz Generation
    Frontend->>FastAPI: GET /pdf/create-quiz/{pdf_id}
    FastAPI->>GeminiAI: Generates Quiz Questions
    FastAPI->>MongoDB: Saves Quiz
    User->>Frontend: Request Quiz
    Frontend->>FastAPI: GET /pdf/get-quiz/{pdf_id}
    FastAPI->>MongoDB: Retrieves Quiz
    FastAPI->>Frontend: Returns Quiz
    Frontend->>User: Displays Quiz
