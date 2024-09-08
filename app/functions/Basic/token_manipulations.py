from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from time import time
from typing import Optional
from .database import SessionLocal
from .models import User

SECRET_KEY = "Sandzharitto_de_kameniavo"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: Optional[int] = None):
    to_encode = data.copy()
    expire = time() + (expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES) * 60
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def check_and_get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expire: float = payload.get("exp")
        if expire is None or time() > expire:
            raise credentials_exception 
        
        id: int = payload.get("id")
        if id is None:
            raise credentials_exception 

        user = db.query(User).filter(User.id == id).first()
        if user is None:
            raise credentials_exception  
        return user

    except JWTError:
        raise credentials_exception
