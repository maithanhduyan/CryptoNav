# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app import config

# Tạo engine kết nối tới cơ sở dữ liệu (SQLAlchemy 2.x)
engine = create_engine(config.DATABASE_URL, future=True)  # future=True cho SQLAlchemy 2.x

# Tạo sessionmaker để tạo Session cho mỗi phiên làm việc
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class cho các model ORM
Base = declarative_base()

# Dependency: Lấy session database cho mỗi request (dùng với FastAPI Depends)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
