from .Basic.models import Comment
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status, APIRouter,Body
from sqlalchemy.orm import Session
from .Basic.token_manipulations import check_and_get_current_user, get_db
from .Basic.models import User, Club, Book, Responses
from .Basic.int_to_string import int_to_string
from typing import List,Optional
from datetime import datetime



comments_routes = APIRouter()






@comments_routes.get("/comments")
def get_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    return comments

@comments_routes.get("/comments")
def add_comments(post_id: int, content: str, db: Session = Depends(get_db)):
    new_comment = Comment(post_id=post_id, content=content)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment



