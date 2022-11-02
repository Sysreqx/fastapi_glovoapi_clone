from typing import Optional
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app import models
from app.database import engine, SessionLocal
from app.routers.auth import get_password_hash, get_current_user, get_user_exception, verify_password

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)


class User(BaseModel):
    username: str
    email: Optional[str]
    firstname: str
    lastname: str
    password: str


class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Users).all()


@router.post("/create/user")
async def create_new_user(create_user: User, db: Session = Depends(get_db)):
    create_user_model = models.Users()

    create_user_model.username = create_user.username
    create_user_model.email = create_user.email
    create_user_model.firstname = create_user.firstname
    create_user_model.lastname = create_user.lastname

    hash_password = get_password_hash(create_user.password)

    create_user_model.hashed_password = hash_password
    create_user_model.is_active = True

    db.add(create_user_model)
    db.commit()


@router.get("/user/")
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user_model is not None:
        return user_model
    return "Invalid user id"


@router.get("/{user_id}")
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user_model = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user_model is not None:
        return user_model
    return "Invalid user id"


@router.put("/update_my_password")
async def update_user_password(user_verification: UserVerification,
                               user: dict = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    user_model = db.query(models.Users) \
        .filter(models.Users.id == user.get("id")) \
        .first()

    if user_model is not None:
        if user_verification.username == user_model.username and verify_password(
                user_verification.password,
                user_model.hashed_password):

            user_model.hashed_password = get_password_hash(user_verification.new_password)
            db.add(user_model)
            db.commit()

            return successful_response(200)
    return "Invalid user or request"


@router.delete("/delete_me")
async def update_user(user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    user_model = db.query(models.Users) \
        .filter(models.Users.id == user.get("id")) \
        .first()

    if user_model is None:
        return http_exception()

    db.query(models.Users).filter(models.Users.id == user.get("id")).delete()

    db.commit()

    return successful_response(201)


def successful_response(status_code: int):
    return {
        "status": status_code,
        "transaction": "Successful"
    }


def http_exception():
    return HTTPException(status_code=404, detail="User not found")
