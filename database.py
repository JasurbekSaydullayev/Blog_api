from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

SQLALCHEMY_DATABASE_URL = DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, echo=True,
    pool_size=30,
    pool_timeout=5
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
