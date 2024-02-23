from typing import List, Optional

from datetime import datetime

from pydantic import BaseModel, constr


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str


class UserView(UserBase):
    username: str
    created_at: datetime
    updated_at: datetime


class UserCreate(UserBase):
    username: str
    password: str


class UserUpdate(UserBase):
    pass


class BlogBase(BaseModel):
    title: str
    description: str
    owner_name: str
    tags: List[str] = None


class BlogView(BlogBase):
    id: int
    created_at: datetime
    updated_at: datetime
    views: int


class BlogCreate(BlogBase):
    pass


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

