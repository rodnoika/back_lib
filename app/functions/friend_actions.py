from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .Basic.token_manipulations import check_and_get_current_user, get_db
from .Basic.models import User
from typing import Optional


class UserBaseModel(BaseModel):
    id: int
    name: str
    surname: str
    profile_picture: Optional[str] 
    score: int

class FriendM(BaseModel):
    friend_id: int

class UserM(BaseModel):
    user_id: int


friend_actions_routes = APIRouter()

@friend_actions_routes.get("/api/social/friends")
def show_friends(current_user: User = Depends(check_and_get_current_user)):
    db = next(get_db())
    if not current_user.friend_ids:
        return {"friends": []}
    friend_ids = [int(friend_id) for friend_id in current_user.friend_ids.split(" ")]

    friends = db.query(User).filter(User.id.in_(friend_ids)).all()
    friends_list = [{"id": friend.id, "name": friend.name, "surname": friend.surname} for friend in friends]

    return {"friends": friends_list}


@friend_actions_routes.post("/api/social/friends/add")
def add_friend(
    data:FriendM,
    current_user: User = Depends(check_and_get_current_user),
    db: Session = Depends(get_db)
):
    friend_id = data.friend_id
    friend = db.query(User).filter(User.id == friend_id).first()
    if not friend:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friend not found")
    if current_user.friend_ids is None:
        current_user.friend_ids = ""
    friend_ids_list = current_user.friend_ids.split(" ")
    if str(friend_id) in friend_ids_list:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a friend")
    if current_user.friend_ids:
        current_user.friend_ids += f" {friend_id}"
    else:
        current_user.friend_ids = str(friend_id)
    db.commit()
    db.refresh(current_user)
    
    return {"detail": "Friend added successfully"}


@friend_actions_routes.post("/api/social/friends/remove")
def remove_friend(data:FriendM, current_user: User = Depends(check_and_get_current_user), db: Session = Depends(get_db)):
    friend_id = data.friend_id
    friend = db.query(User).filter(User.id == friend_id).first()
    if not friend:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friend not found")
    if str(friend_id) not in current_user.friend_ids.split(" "):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a friend")
    friend_ids_list = current_user.friend_ids.split(" ")
    friend_ids_list.remove(str(friend_id))
    current_user.friend_ids = " ".join(friend_ids_list)
    db.commit()
    db.refresh(current_user)
    return {"detail": "Friend removed successfully"}

@friend_actions_routes.get("/api/person/user-info", response_model=UserBaseModel)
def get_user_info(data:UserM):
    user_id = data.user_id
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(418, "No such teapot found")

    return UserBaseModel(
        id=user.id, 
        name=user.name,
        surname=user.surname,
        profile_picture=user.profile_picture or "", 
        score=user.score
    )
