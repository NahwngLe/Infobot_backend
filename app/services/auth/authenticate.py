from fastapi import HTTPException
from passlib.context import CryptContext
from app.database import *
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def authenticate_user(username, password):
    query = {"username": username}
    user = db.users.find_one(query)
    if not user:
        return False
    if not bcrypt_context.verify(password, user["hash_password"]):
        return  False
    return user