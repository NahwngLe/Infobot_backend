from fastapi import APIRouter, UploadFile, File, HTTPException, Response, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

import hashlib
from bson import ObjectId

from app.database import *
from app.services.auth.authenticate import authenticate_user
from app.services.auth.createToken import create_access_token

import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["AUTH"])

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 10000

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class UserRequest(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    user_id: str

class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/register")
def register_account(data: UserRequest):
    query = {"username": data.username}
    result = db.users.find_one(query)

    if result:
        return {"isExist": True ,"message": "Username already exist"}

    hash_password = bcrypt_context.hash(data.password)
    user_id = hashlib.sha256(data.username.encode()).hexdigest()
    db.users.insert_one({"username": data.username,
                         "user_id": user_id,
                         "hash_password": hash_password,
                         "date_create": datetime.now(timezone.utc)})
    return {"message": "Create account successfully"}

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(
            data={"sub": user["username"], "user_id": str(user["user_id"])},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=User)
async def read_users_me(token: str = Depends(oauth2_bearer)):
    try:
        print("payload login")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Hết payload login")
        username: str = payload.get("sub")
        print("username", username)
        user_id: str = payload.get("user_id")
        print("user_id", user_id)
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return User(username=username, user_id=user_id)