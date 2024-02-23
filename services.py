import hashlib
from fastapi import HTTPException

from sqlalchemy.orm import Session

from schemas import UserCreate, UserUpdate, UserBase, UserChangePassword
from models import User, Blog, Comment, Tag
from validators import check_strong_password, check_phone_number


# Password
def hash_password(password):
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()


def verify_password(password, hashed_password):
    return hash_password(password) == hashed_password


# CRUD USER
def _create_user(db: Session, user: UserCreate):
    user = User(**user.dict())
    check_username = db.query(User).filter(User.username == user.username).first()
    if check_username:
        raise HTTPException(status_code=404, detail="Username already exists")
    check_email = db.query(User).filter(User.email == user.email).first()
    if check_email:
        raise HTTPException(status_code=404, detail="Email already exists")
    check_phone_number(user.phone_number)
    check_phone_number2 = db.query(User).filter(User.phone_number == user.phone_number).first()
    if check_phone_number2:
        raise HTTPException(status_code=400, detail="Phone number already exists")
    if not check_strong_password(user.password):
        raise HTTPException(status_code=400, detail="Password is very easy to hack")
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


def _update_user(db: Session, username, user: UserUpdate):
    user_ = db.query(User).filter(User.username == username).first()
    if not user_:
        raise HTTPException(status_code=404, detail="User not found")
    check_email = db.query(User).filter(User.email == user.email).first()
    if check_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    check_number = db.query(User).filter(User.phone_number == user.phone_number).first()
    if check_number:
        raise HTTPException(status_code=400, detail="Phone number already exists")
    user_.first_name = user.first_name
    user_.last_name = user.last_name
    user_.email = user.email
    user_.phone_number = user.phone_number
    db.merge(user_)
    db.commit()
    db.refresh(user_)
    return user_


def _change_password(db: Session, username: str, passwords: UserChangePassword):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(passwords.old_password, user.password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    if passwords.new_password != passwords.confirm_password:
        raise HTTPException(status_code=400, detail="New password and Confirm password are different")
    if not check_strong_password(passwords.new_password):
        raise HTTPException(status_code=400, detail="Password is very easy to hack. "
                                                    "Password must have more than 8 characters, "
                                                    "at least one uppercase letter, "
                                                    "at least one lowercase letter and "
                                                    "at least one number")
    user.password = hash_password(passwords.new_password)
    db.merge(user)
    db.commit()
    return "Password changed successfully"


def _delete_user(db, username, password):
    user = User.query.filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Password is incorrect")
    db.delete(user)
    db.commit()
    return "User deleted successfully"


# CRUD BLOG
def _create_blog(db, blog):
    user = db.query(User).filter(User.username == blog.owner_name).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    blog_ = Blog(owner_name=blog.owner_name, title=blog.title,
                 description=blog.description)
    db.add(blog_)
    db.commit()
    db.refresh(blog_)
    for tag in blog.tags:
        db.add(Tag(name=tag, blog_id=blog_.id))
        db.commit()
    temp = blog_.get_dict()
    temp['tags'] = [tag for tag in blog.tags]
    return temp


def _get_blogs(db, skip, limit):
    blogs = db.query(Blog).offset(skip).limit(limit).all()
    if not blogs:
        raise HTTPException(status_code=404, detail="Blogs do not found")
    temp = []
    for blog in blogs:
        qwe = blog.get_dict()
        tags_ = db.query(Tag).filter(Tag.blog_id == blog.id).all()
        qwe['tags'] = [tag.name for tag in tags_]
        temp.append(qwe)
    return temp


def _get_blog(db, blog_id):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    blog.views += 1
    db.merge(blog)
    db.commit()
    temp = blog.get_dict()
    tags = db.query(Tag).filter(Tag.blog_id == blog.id).all()
    temp['tags'] = [tag.name for tag in tags]
    return temp
