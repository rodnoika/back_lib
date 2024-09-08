from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import RedirectResponse, PlainTextResponse, FileResponse
from typing import Annotated
from app.functions.Basic.database import Base, engine
from app.functions.Basic.models import User, Book, Responses
from fastapi.middleware.cors import CORSMiddleware
from app.functions.authorization import autorization_router
from app.functions.friend_actions import friend_actions_routes
from app.functions.Exchange_Books import Exchange_routes
from app.functions.Club_actions import club_actions_routes


app = FastAPI()
app.include_router(autorization_router)
app.include_router(friend_actions_routes)
app.include_router(Exchange_routes)
app.include_router(club_actions_routes)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



if (__name__=="__main__"):
    import uvicorn
    uvicorn.run(app=app, host="127.0.0.1", port=8000)