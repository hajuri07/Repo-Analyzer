from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException, status
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import Depends
from sqlalchemy.orm import Session

from .database import get_db
from . import models


password_hasher = PasswordHash((Argon2Hasher(),))

def hash_password(password:str)->str:
    return password_hasher.hash(password)

def verify_password(original_pass:str , hashed_pass:str)->bool:
    try:
        
        return password_hasher.verify(original_pass, hashed_pass)
    except Exception:
        return False
    
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def create_access_token(user_id: int) -> str:
   
    expiry_time = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    
    payload = {
        "sub": str(user_id),   #
        "exp": expiry_time  
    }
    
    
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_access_token(token: str):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        
        user_id = payload.get("sub")
        
        
        if user_id is None:
            raise credentials_exception
            
        
        return int(user_id)
        
    except JWTError:
        
        raise credentials_exception
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
        user_id = verify_access_token(token)
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found"
                )

        return user

