import hashlib

from sqlalchemy.orm import Session

from models import User, Blog, Comment, Tag


def hash_password(password):
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()


def verify_password(password, hashed_password):
    return hash_password(password) == hashed_password




