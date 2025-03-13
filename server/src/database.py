# src/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import settings

# Tạo engine với DATABASE_URL từ config
# Nếu sử dụng SQLite, cần cấu hình thêm đối số "check_same_thread"
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    ),
)

# Tạo session factory cho việc tương tác với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho các model
Base = declarative_base()


# Dependency cho FastAPI: tạo session và tự động đóng session sau khi sử dụng
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
