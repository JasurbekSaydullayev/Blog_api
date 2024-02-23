import hashlib
from fastapi import HTTPException

from sqlalchemy.orm import Session

from schemas import UserCreate, UserUpdate, UserBase
from models import User, Blog, Comment, Tag


def hash_password(password):
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()


def verify_password(password, hashed_password):
    return hash_password(password) == hashed_password


def _create_user(db: Session, user: UserCreate):
    user = User(**user.dict())
    check_username = db.query(User).filter(User.username == user.username).first()
    if check_username:
        raise HTTPException(status_code=404, detail="Username already exists")
    check_email = db.query(User).filter(User.email == user.email).first()
    if check_email:
        raise HTTPException(status_code=404, detail="Email already exists")
    user.password = hash_password(user.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _get_users(db: Session,
               skip: int = 0,
               limit: int = 10):
    users = db.query(User).offset(skip).limit(limit).all()
    if not users:
        raise HTTPException(status_code=404, detail="Users not found")
    return users


def _get_user(db: Session,
              username: str):
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


async def _update_user(db: Session, username, user: UserUpdate):
    user_ = db.query(User).filter(User.username == username).first()
    if not user_:
        raise HTTPException(status_code=404, detail="User not found")
    check_email = db.query(User).filter(User.email == user.email).first()
    if check_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    user_.first_name = user.first_name
    user_.last_name = user.last_name
    user_.email = user.email
    db.merge(user_)
    db.commit()
    db.refresh(user_)
    return user_



