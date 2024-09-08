from .Basic.models import Comments
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status, APIRouter,Body
from sqlalchemy.orm import Session
from .Basic.token_manipulations import check_and_get_current_user, get_db
from .Basic.models import User, Club, Book
from .Basic.int_to_string import int_to_string
from typing import List,Optional

comments_routes = APIRouter()

class CommentBase(BaseModel):
    content: str
    user_name: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    post_id: int

    class Config:
        orm_mode = True

class bookModel(BaseModel):
    id:int

class ResponceModel(BaseModel):
    id: int
    author_id: int
    date: str
    text: str

class ResponcecModel(BaseModel):
    resps:list[ResponceModel]

@comments_routes.get("/api/get_responces")
def get_responces(bookie : bookModel, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id==bookie.id).first()
    if book is None:
        raise HTTPException(418, "no such book found")
    if book.Responce_id is None:
        raise HTTPException(418, "no responces for the book")
    while True:




def create_comment(db: Session, comment: CommentCreate, post_id: int):
    db_comment = Comment(**comment.model_dump(), post_id=post_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment



