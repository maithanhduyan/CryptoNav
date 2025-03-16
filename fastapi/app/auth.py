# app/auth.py
from datetime import datetime, timedelta, timezone

import jwt  # PyJWT library
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import bcrypt
from app import config, model, database

# Schema OAuth2PasswordBearer để lấy token từ Header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def create_access_token(data: dict, expires_delta: int = None):
    """Tạo JWT token từ thông tin người dùng."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    # Sinh token JWT
    encoded_jwt = jwt.encode(
        to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu plaintext với mật khẩu đã băm."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Băm mật khẩu (hash password) để lưu vào DB."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def get_current_user(
    db: database.SessionLocal = Depends(database.get_db),
    token: str = Depends(oauth2_scheme),
):
    """Dependency: Lấy đối tượng User hiện tại dựa trên JWT token."""
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(
            token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
        )
        username: str = payload.get(
            "sub"
        )  # 'sub' sẽ chứa định danh người dùng (vd: username)
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # Lấy người dùng từ DB
    user = db.query(model.User).filter(model.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
