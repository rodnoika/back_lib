from fastapi import FastAPI, HTTPException, Depends, APIRouter
from pydantic import BaseModel
from typing import List
from app.functions.Basic.database import SessionLocal
from dotenv import load_dotenv
import aiohttp
import asyncpg
import hashlib
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://api.gemini.com/generate-quiz"

Games_routers = APIRouter()

class QuizRequest(BaseModel):
    text: str
    num_questions: int 

class QuizQuestion(BaseModel):
    question: str
    answers: List[str]
    correct_answer: str 

class QuizResponse(BaseModel):
    questions: List[QuizQuestion]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@Games_routers.post("/api/generate_quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest, db=Depends(get_db)):
    text_hash = hashlib.md5(request.text.encode()).hexdigest()

    quiz_data = await db.fetchval("SELECT quiz FROM quizzes WHERE text_hash = $1", text_hash)
    if quiz_data:
        return QuizResponse(questions=quiz_data)

    async with aiohttp.ClientSession() as session:
        async with session.post(GEMINI_API_URL, headers={
            "Authorization": f"Bearer {GEMINI_API_KEY}",
            "Content-Type": "application/json"
        }, json={"text": request.text, "num_questions": request.num_questions}) as response:  # Передаем количество вопросов
            if response.status == 200:
                quiz_data = await response.json()

                await db.execute(
                    "INSERT INTO quizzes (text_hash, quiz) VALUES ($1, $2)",
                    text_hash, quiz_data
                )

                return QuizResponse(questions=quiz_data)
            else:
                error_message = await response.text()
                raise HTTPException(status_code=response.status, detail=f"Ошибка Gemini API: {error_message}")

@Games_routers.post("/api/check_answer")
def check_answer(question_id: int, user_answer: str, db: SessionLocal = Depends(get_db)):
    question = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
    
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if question.correct_answer == user_answer:
        return {"result": "correct"}
    else:
        return {"result": "incorrect"}
