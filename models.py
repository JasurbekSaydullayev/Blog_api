import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)


class Blog(Base):
    __tablename__ = 'blogs'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    owner_name = Column(String, ForeignKey('users.username'))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)
    views = Column(Integer, default=0)


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    blog_id = Column(Integer, ForeignKey('blogs.id'))


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey('users.username'))
    blog_id = Column(Integer, ForeignKey('blogs.id'))
    content = Column(String)
    created_at = Column(DateTime, default=datetime.time)
    updated_at = Column(DateTime, default=datetime.time)
