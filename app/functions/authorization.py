from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, PlainTextResponse
from sqlalchemy.orm import Session
from .Basic.token_manipulations import check_and_get_current_user, create_access_token, get_db
from pydantic import BaseModel
from .Basic.models import User
from typing import Optional


autorization_router = APIRouter()

class RegistrationResponse(BaseModel):
    success: bool
class TokenResponse(BaseModel):
    token: str
    token_type: str
class UserCreate(BaseModel):
    name: str
    surname: str
    password: str
    email:str
    date_of_birth : str

class UserInDB(BaseModel):
    id: int
    email: str
    name: str
    surname: str
    date_of_birth: str
    profile_picture: Optional[str] = None
    invations: Optional[str] = None
    score: int

@autorization_router.post("/api/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")
    

    db_user = User(email=user.email,name=user.name, surname=user.surname, date_of_birth=user.date_of_birth, password=user.password,)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return RegistrationResponse(success=True)

@autorization_router.post("/api/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == form_data.username).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such email has registered")
    if db_user.password != form_data.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password is not correct")
    token = create_access_token({"id": db_user.id})
    return {"token": token, "token_type": "bearer"}

@autorization_router.get("/api/user/me", response_model=UserInDB)
def get_current_user(current_user: User = Depends(check_and_get_current_user)):
    return UserInDB(
        id = current_user.id,
        email=current_user.email,
        name=current_user.name,
        surname=current_user.surname,
        password=current_user.password,
        profile_picture=current_user.profile_picture,
        date_of_birth=current_user.date_of_birth,
        score = current_user.score,
        invations = current_user.invations
    )

