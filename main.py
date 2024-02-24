import secrets
from typing import Annotated, List

from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, status, HTTPException, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials

import schemas
from config import ADMIN_USERNAME, ADMIN_PASSWORD
from services import _create_user, _get_users, _get_user, _update_user, _change_password, _delete_user, _create_blog, \
    _get_blogs, _get_blog, _update_blog
from database import SessionLocal
from schemas import UserCreate, UserUpdate, UserBase, UserView, UserChangePassword

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


# USER
@app.get('/users/', response_model=List[UserView], tags=["Users"])
def get_users(q: Annotated[str, Depends(get_current_username)],
              db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    return _get_users(db, skip, limit)


@app.get('/user/{username}', response_model=UserView, tags=["Users"])
def get_user(username: str,
             q: Annotated[str, Depends(get_current_username)],
             db: Session = Depends(get_db)):
    return _get_user(db, username)


@app.post('/user-create/', response_model=UserBase, tags=["Users"])
def create_user(q: Annotated[str, Depends(get_current_username)],
                user: UserCreate,
                db: Session = Depends(get_db)):
    return _create_user(db=db, user=user)


@app.put('/user-update/{username}', response_model=UserView, tags=["Users"])
def update_user(username: str,
                q: Annotated[str, Depends(get_current_username)],
                user: UserUpdate,
                db: Session = Depends(get_db)):
    return _update_user(db=db, username=username, user=user)


@app.put("/user/{username}/password-change", tags=["Users"])
def change_password(username: str,
                    passwords: schemas.UserChangePassword,
                    q: Annotated[str, Depends(get_current_username)],
                    db: Session = Depends(get_db)):
    return _change_password(db=db, username=username, passwords=passwords)


@app.delete('/user-delete/{username}', tags=["Users"])
def delete_user(username: str,
                q: Annotated[str, Depends(get_current_username)],
                password: str = Form(...),
                db: Session = Depends(get_db), ):
    return _delete_user(db=db, username=username, password=password)


# BLOG
@app.post('/blog-create/', response_model=schemas.BlogView, tags=["Blogs"])
def create_blog(blog: schemas.BlogCreate,
                db: Session = Depends(get_db)):
    return _create_blog(db, blog)


@app.get('/blogs-list-view', response_model=list[schemas.BlogView], tags=["Blogs"])
def get_blogs(db: Session = Depends(get_db),
              skip: int = 0,
              limit: int = 10):
    return _get_blogs(db, skip, limit)


@app.get('/blog/{blog_id}', response_model=schemas.BlogView, tags=["Blogs"])
def get_blog(blog_id: int,
             db: Session = Depends(get_db)):
    return _get_blog(db, blog_id)


@app.put('/blog-update/{blog_id}', response_model=schemas.BlogView, tags=["Blogs"])
def update_blog(blog_id: int,
                username: str = Form(...),
                password: str = Form(...),
                title: str = Form(...),
                description: str = Form(...),
                tags: List[str] = Form(...),
                db: Session = Depends(get_db)):
    return _update_blog(db, blog_id, username,
                        password, title, description, tags)
