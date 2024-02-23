from typing import List
from datetime import datetime

from pydantic import BaseModel, EmailStr


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


class UserUpdate(UserBase):
    pass


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str


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


class BlogCreate(BlogBase):
    tags: List[str] = None
    owner_name: str


class BlogUpdate(BlogBase):
    pass


class CommentBase(BaseModel):
    username: str
    blog_id: int
    content: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    pass


class CommentView(CommentBase):
    id: int
    created_at: str
    updated_at: str
