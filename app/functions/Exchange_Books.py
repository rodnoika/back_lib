from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from .Basic.models import User, Book
from .Basic.token_manipulations import check_and_get_current_user, get_db

Exchange_routes = APIRouter()

@Exchange_routes.post("/api/add_book_to_library")
def add_book_to_library(book_id: int, current_user: User = Depends(check_and_get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book in user.books:
        raise HTTPException(status_code=400, detail="Book already in user's library")

    user.books.append(book)
    db.commit()
    return {"message": "Book added to user successfully"}

@Exchange_routes.post("/api/remove_from_library")
def remove_from_library(book_id: int, current_user: User = Depends(check_and_get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book not in user.books:
        raise HTTPException(status_code=400, detail="Book not in user's library")

    user.books.remove(book)
    db.commit()
    return {"message": "Book removed from user successfully"}
    
@Exchange_routes.get("/api/get_user_library")
def get_user_library(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_books = user.books

    return {"user_id": user.id, "books": [{"id": book.id, "title": book.name} for book in user_books]}

@Exchange_routes.get("/api/check_book_in_library")
def check_book_in_library(user_id: int, book_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book in user.books:
        return {"message": "Book is in user's library"}
    else:
        return {"message": "Book is not in user's library"}

@Exchange_routes.post("/api/add_book")
def add_book(title: str, author: str, db: Session = Depends(get_db)):
    new_book = Book(title=title, author=author)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return {"message": "Book added successfully", "book": {"id": new_book.id, "title": new_book.title, "author": new_book.author}}
