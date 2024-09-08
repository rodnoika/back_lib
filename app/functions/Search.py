from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from .Basic.models import Club, User, Book
from .Basic.database import get_db

search_routes = APIRouter()
@search_routes.get("/api/search/all-items")
def get_all_items(db: Session = Depends(get_db)):
    clubs = db.query(Club).all()
    users = db.query(User).all()
    books = db.query(Book).all()
    result = []
    for club in clubs:
        result.append({"id": club.id, "name": club.name})
    
    for user in users:
        result.append({"id": user.id, "name": user.name})
    
    for book in books:
        result.append({"id": book.id, "name": book.name})
    
    return result