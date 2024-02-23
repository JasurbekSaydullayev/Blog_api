import secrets
from typing import Annotated, List

from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, status, HTTPException, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from config import ADMIN_USERNAME, ADMIN_PASSWORD
from services import _create_user, _get_users, _get_user, _update_user
from database import SessionLocal
from schemas import UserCreate, UserUpdate, UserBase, UserView

app = FastAPI()

security = HTTPBasic()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_username(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    current_username_bytes = credentials.username.encode("utf-8")
    correct_username_bytes = ADMIN_USERNAME.encode("utf-8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf-8")
    correct_password_bytes = ADMIN_PASSWORD.encode("utf-8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get('/users/', response_model=List[UserView])
def get_users(q: Annotated[str, Depends(get_current_username)],
              db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    return _get_users(db, skip, limit)


@app.get('/user/{username}', response_model=UserView)
def get_user(username: str,
             q: Annotated[str, Depends(get_current_username)],
             db: Session = Depends(get_db)):
    return _get_user(db, username)


@app.post('/user-create/', response_model=UserBase)
def create_user(q: Annotated[str, Depends(get_current_username)],
                user: UserCreate,
                db: Session = Depends(get_db)):
    return _create_user(db=db, user=user)


@app.put('/user-update/{username}', response_model=UserView)
async def update_user(username: str,
                      q: Annotated[str, Depends(get_current_username)],
                      user: UserUpdate,
                      db: Session = Depends(get_db)):
    return await _update_user(db=db, username=username, user=user)
