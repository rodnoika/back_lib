from fastapi import Depends, HTTPException, APIRouter,UploadFile, File,Form
from sqlalchemy.orm import Session
from .Basic.models import User, Book
from .Basic.token_manipulations import check_and_get_current_user, get_db
from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime
import base64




Exchange_routes = APIRouter()
class bookM(BaseModel):
    book_id: int

class userM(BaseModel):
    user_id: int

@Exchange_routes.post("/api/add_book_to_library")
def add_book_to_library(data:bookM, current_user: User = Depends(check_and_get_current_user), db: Session = Depends(get_db)):
    book_id = data.book_id
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book in current_user.books:
        raise HTTPException(status_code=400, detail="Book already in user's library")

    current_user.books.append(book)
    db.commit()
    return {"message": "Book added to user successfully"}

@Exchange_routes.post("/api/remove_from_library")
def remove_from_library(data:bookM, current_user: User = Depends(check_and_get_current_user), db: Session = Depends(get_db)):
    book_id = data.book_id
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
def get_user_library(current_user: User = Depends(check_and_get_current_user)):
    db: Session = next(get_db())
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_books = user.books

    return {"user_id": user.id, "books": [{"id": book.id, "title": book.name} for book in user_books]}

@Exchange_routes.get("/api/check_book_in_library")
def check_book_in_library(data:userM, book_id: int, db: Session = Depends(get_db)):
    user_id=data.user_id
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
class Exchange(BaseModel):
    title: str
    author: str
    file: Optional[UploadFile] = File(None)

@Exchange_routes.post("/api/add_book")
async def add_book(
    name: str = Form(...),
    description: str = Form(...),
    date_of_publication: str = Form(...),  # Date as string
    picture: Optional[UploadFile] = File(None),
    book_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        date_of_publication_date = datetime.strptime(date_of_publication, '%Y-%m-%d').date()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    new_book = Book(
        name=name,
        description=description,
        date_of_publication=date_of_publication_date
    )
    
    if picture:
        picture_content = await picture.read()
        picture_base64 = base64.b64encode(picture_content).decode('utf-8')
        new_book.picture = picture_base64

    if book_file:
        book_file_content = await book_file.read()
        book_file_base64 = base64.b64encode(book_file_content).decode('utf-8')
        new_book.book_file = book_file_base64

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return {"message": "Book added successfully", "book": {"id": new_book.id, "name": new_book.name, "description": new_book.description}}

class BookResponse(BaseModel):
    id: int
    name: str
    description: str
    date_of_publication: Optional[str] = None 
    picture: Optional[str] = None
    book_file: Optional[str] = None
    stars: int
    Responce_id: Optional[int]

    class Config:
        orm_mode = True


@Exchange_routes.get("/api/books", response_model=List[BookResponse])
def get_books(limit: int = 5, db: Session = Depends(get_db)):
    books = db.query(Book).limit(limit).all()
    if not books:
        raise HTTPException(status_code=404, detail="No books found")

    books_response = []
    for book in books:
        books_response.append(
            BookResponse(
                id=book.id,
                name=book.name,
                description=book.description,
                date_of_publication=book.date_of_publication.isoformat() if book.date_of_publication else None,
                picture=book.picture,
                book_file=book.book_file,
                stars=book.stars,
                Responce_id=book.Responce_id
            )
        )
    
    return books_response

