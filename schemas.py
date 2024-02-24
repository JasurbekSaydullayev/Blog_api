from typing import List
from datetime import datetime

from pydantic import BaseModel, EmailStr


# USER
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str


class UserView(UserBase):
    username: str
    created_at: datetime
    updated_at: datetime


class UserCreate(UserBase):
    username: str
    password: str


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str


# BLOG
class BlogBase(BaseModel):
    title: str
    description: str


class BlogView(BlogBase):
    tags: List[str] = None
    id: int
    owner_name: str
    created_at: datetime
    updated_at: datetime
    views: int


# COMMENT
class CommentBase(BaseModel):
    id: int
    username: str
    blog_id: int
    content: str


class CommentView(CommentBase):
    created_at: datetime
    updated_at: datetime
