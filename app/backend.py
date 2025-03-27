from fastapi import FastAPI
from app.routers import pdf

app = FastAPI()

#Tich hop router
app.include_router(pdf.router)