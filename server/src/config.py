# src/config.py
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Ví dụ: sử dụng SQLite cho môi trường development
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cryptonav.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        # Nếu có file .env, tự động đọc biến môi trường từ đó
        env_file = ".env"


# Khởi tạo đối tượng settings để sử dụng ở các module khác
settings = Settings()
