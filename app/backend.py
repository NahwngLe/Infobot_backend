from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import pdf, auth
from app.database import client

from prometheus_fastapi_instrumentator import Instrumentator
import os
import uvicorn

app = FastAPI()

Instrumentator().instrument(app).expose(app)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://frontend:5173"],  # Chỉ cho phép frontend Vite
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các phương thức (GET, POST, PUT, DELETE...)
    allow_headers=["*"],  # Cho phép tất cả các headers
)

#Tich hop router
app.include_router(pdf.router)
app.include_router(auth.router)
@app.on_event("shutdown")
def shutdown_db():
    client.close()  # Đóng connection

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)