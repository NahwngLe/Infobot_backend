from fastapi import FastAPI
from app.routers import pdf
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Chỉ cho phép frontend Vite
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các phương thức (GET, POST, PUT, DELETE...)
    allow_headers=["*"],  # Cho phép tất cả các headers
)

#Tich hop router
app.include_router(pdf.router)