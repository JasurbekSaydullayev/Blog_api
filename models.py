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
    phone_number = Column(String, unique=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)

    def __str__(self):
        return self.username


class Blog(Base):
    __tablename__ = 'blogs'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    owner_name = Column(String, ForeignKey('users.username'))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)
    views = Column(Integer, default=0)

    def __str__(self):
        return self.title

    def get_dict(self):
        return {"id": self.id, "title": self.title,
                "description": self.description,
                "owner_name": self.owner_name,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "views": self.views}


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    blog_id = Column(Integer, ForeignKey('blogs.id', ondelete="CASCADE"))

    def __str__(self):
        return self.name


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey('users.username'))
    blog_id = Column(Integer, ForeignKey('blogs.id'))
    content = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)

    def __str__(self):
        return self.content
