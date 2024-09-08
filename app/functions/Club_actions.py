from fastapi import Depends, HTTPException, status, APIRouter,Body
from sqlalchemy.orm import Session
from .Basic.token_manipulations import check_and_get_current_user, get_db
from .Basic.models import User, Club
from pydantic import BaseModel
from typing import List,Optional

club_actions_routes = APIRouter()

class ClubBaseModel(BaseModel):
    id: int
    name: str
    description: str
    isprivate: bool
    owner_id: int
class CreateClubRequest(BaseModel):
    name: str
    description: str
    isPrivate: bool

class ClubsResponse(BaseModel):
    clubs: List[ClubBaseModel]

@club_actions_routes.get("/api/social/my-clubs", response_model=ClubsResponse)
def show_clubs(current_user: User = Depends(check_and_get_current_user)):
    db: Session = next(get_db())
    club_list = db.query(Club).join(Club.users).filter(User.id == current_user.id).all()
    
    if not club_list:
        return ClubsResponse(clubs=[])
    
    club_data = [
        ClubBaseModel(
            id=club.id,
            name=club.name,
            description=club.description,
            isprivate=club.is_private,
            owner_id=club.owner_id
        ) for club in club_list
    ]
    
    return ClubsResponse(clubs=club_data)
    
class CreateClubRequest(BaseModel):
    name: str
    description: str
    is_private: bool

@club_actions_routes.post("/api/social/create-club")
def create_club(
    club_datas: CreateClubRequest,
    current_user: User = Depends(check_and_get_current_user),
    db: Session = Depends(get_db)
):
    name = club_datas.name
    description = club_datas.description
    isPrivate = club_datas.is_private

    existing_club = db.query(Club).filter(Club.name == name).first()
    if existing_club:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Club with this name already exists")

    new_club = Club(
        name=name,
        description=description,
        is_private=isPrivate,
        owner_id=current_user.id,
        users=[current_user]
    )
    db.add(new_club)
    db.commit()
    db.refresh(new_club)

    return new_club

class AloneC(BaseModel):
    club_id:int

class Chenge(BaseModel):
    club_id:int
    description:Optional[str] = None
    isprivate:Optional[bool] = None



@club_actions_routes.get("/api/social/club-info/{club_id}", response_model=ClubBaseModel)
def get_club_info(club_id: int, db: Session = Depends(get_db)):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such club found")
    return ClubBaseModel(
        id=club.id,
        name=club.name,
        description=club.description,
        isprivate=club.is_private,
        owner_id=club.owner_id
    )

@club_actions_routes.post("/api/social/clubs/change")
def change(datas:Chenge, current_user: User = Depends(check_and_get_current_user)):
    club_id = datas.club_id
    description = datas.description
    isprivate = datas.isprivate
    db = next(get_db())
    club = db.query(Club).filter(Club.id==club_id).first()
    if not club:
        raise HTTPException(418, "No such club found")
    if club.owner_id != current_user.id:
        raise HTTPException(418, "Not enogh rights for you, because of your color")
    if  description is not None:
        club.description = description
    if isprivate != None:
        club.is_private = isprivate
    db.commit()
    db.refresh(club)
    return {"detail":"successful"}


class InviteP(BaseModel):
    club_id: int
    user_id: int



@club_actions_routes.post("/api/social/clubs/invite_user")
def invite_user(datas: InviteP, current_user: User = Depends(check_and_get_current_user), db: Session = Depends(get_db)):
    club_id = datas.club_id
    user_id = datas.user_id
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="No such club found")
    if club.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough rights for you to invite users")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="No such user found")
    if user.invations is None:
        user.invations = ""
    if str(club_id) in user.invations.split("."):
        raise HTTPException(status_code=400, detail="User has already been invited")
    if club in user.clubs:
        raise HTTPException(status_code=400, detail="User is already a member of the club")
    user.invations += "." + str(club_id)
    db.commit()
    
    return {"detail": "Successfully invited user"}


@club_actions_routes.post("/api/social/clubs/delete_invation")
def delete_invation_user(datas: InviteP, current_user: User = Depends(check_and_get_current_user), db: Session = Depends(get_db)):
    club_id = datas.club_id
    user_id = datas.user_id
    club = db.query(Club).filter(club.id==club_id).first()
    if not club:
        raise HTTPException(418, "No such club found")
    if club.owner_id != current_user.id:
        raise HTTPException(418, "Not enogh rights for you, because of your color")
    user = db.query(Club).filter(user.id==user_id).first()
    if not user:
        raise HTTPException(418, "No such user found")
    if not user.invations.split(".").count(str(club_id)):
        raise HTTPException(418, "User has not been invited")
    if user.clubs.contains(club):
        raise HTTPException(418, "User is member of the club")
    tmp = current_user.invations.split(".")
    current_user.invations = ""
    tmp.remove(str(club_id))
    for t in tmp:
        current_user.invations += "." + t
    current_user.invations.pop(0)
    return {"detail": "successfuly"}

@club_actions_routes.post("/api/social/clubs/accept_invation")
def accept_invation(data: AloneC, current_user: User = Depends(check_and_get_current_user), db: Session = Depends(get_db)):
    club_id = data.club_id
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(418, "No such club found")
    if club in current_user.clubs:
        raise HTTPException(418, "You are already a member of the club")
    invations_list = [int(inv) for inv in current_user.invations.split(".") ]
    if club_id not in invations_list:
        raise HTTPException(418, "You are not invited")
    invations_list.remove(club_id)
    current_user.invations = ".".join(map(str, invations_list))
    club.users.append(current_user)
    db.commit()
    return {"detail": "Successfully accepted invitation"}

@club_actions_routes.post("/api/social/clubs/decline_invation")
def decline_invation(club_id: int, current_user: User = Depends(check_and_get_current_user), db: Session = Depends(get_db)):
    current_user = db.merge(current_user)

    club = db.query(Club).filter(club.id==club_id).first()
    if not club:
        raise HTTPException(418, "No such club found")
    if not current_user.clubs.contains(club):
        raise HTTPException(418, "you are not a member of the club")
    if current_user.invations.split(".").count(str(club_id)) == 0:
        raise HTTPException(418, "you are not invited")
    tmp = current_user.invations.split(".")
    current_user.invations = ""
    tmp.remove(str(club_id))
    for t in tmp:
        current_user.invations += "." + t
    current_user.invations.pop(0)
    return {"detail": "successfuly"} 

@club_actions_routes.post("/api/social/clubs/delete_user")
def delete_user(datas: InviteP, current_user: User = Depends(check_and_get_current_user), db: Session = Depends(get_db)):
    club_id = datas.club_id
    user_id = datas.user_id
    club = db.query(Club).filter(Club.id==club_id).first()
    if not club:
        raise HTTPException(418, "No such club found")
    if club.owner_id != current_user.id:
        raise HTTPException(418, "Not enogh rights for you, because of your color")
    user = db.query(User).filter(User.id==user_id).first()
    if not user:
        raise HTTPException(418, "No such user found")
    if user not in club.users:
        raise HTTPException(418, "User is not member of the club")
    club.users.remove(user)
    db.commit()
    return {"detail": "successfuly"}