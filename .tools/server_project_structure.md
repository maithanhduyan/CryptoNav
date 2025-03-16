# Cấu trúc Dự án như sau:

```
.\fastapi
├── .chat
│   └── overview.md
├── .devcontainer
│   └── devcontainer.json
├── .dockerignore
├── Dockerfile
├── app
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── crud.py
│   ├── database.py
│   ├── logger.py
│   ├── main.py
│   ├── model.py
│   └── router.py
└── script
    ├── setup.sh
    └── start.sh
```

# Danh sách chi tiết các file:

## File .\fastapi\app\auth.py:
```python
# app/auth.py
from datetime import datetime, timedelta, timezone

import jwt  # PyJWT library
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

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
    # Ở đây dùng giải pháp đơn giản để minh họa, khuyến nghị dùng bcrypt trong thực tế
    import hashlib

    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


def get_password_hash(password: str) -> str:
    """Băm mật khẩu (hash password) để lưu vào DB."""
    import hashlib

    return hashlib.sha256(password.encode()).hexdigest()


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

```

## File .\fastapi\app\config.py:
```python
# app/config.py
import os

# URL kết nối cơ sở dữ liệu từ biến môi trường (với giá trị mặc định trùng với cấu hình docker-compose)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://appuser:apppassword@db:5432/app")

# Cấu hình JWT
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "your-secret-key"
)  # Khóa bí mật để mã hóa JWT
JWT_ALGORITHM = "HS256"  # Thuật toán mã hóa JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Thời gian hết hạn token (30 phút)

# Cấu hình logging: mức log mặc định, sử dụng biến môi trường để dễ thay đổi giữa development và production
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

```

## File .\fastapi\app\crud.py:
```python

```

## File .\fastapi\app\database.py:
```python
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

```

## File .\fastapi\app\logger.py:
```python
# app/logger.py
import logging
import sys
from pythonjsonlogger import jsonlogger  # Thư viện hỗ trợ format JSON (cài qua pip)

from app import config


def setup_logging():
    """Cấu hình logging cho ứng dụng."""
    log_level = config.LOG_LEVEL

    # Tạo logger gốc
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Cấu hình handler gửi log ra stdout
    handler = logging.StreamHandler(sys.stdout)
    # Định dạng log: ở đây dùng JSONFormatter để phù hợp với ELK
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Ví dụ log ban đầu
    logging.info("Logging is configured. Level: %s", log_level)

```

## File .\fastapi\app\main.py:
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.router import users_router, items_router
from app import logger, config, database, model

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="CryptoNav API",
    description="API for managing cryptocurrency portfolios and tracking investments",
    version="1.0.0",
)

# Cấu hình CORS (nếu cần thiết cho front-end)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép mọi domain (cân nhắc thu hẹp trong production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to CryptoNav API",
        "documentation": "/docs",
        "redoc": "/redoc",
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


# Gắn các router cho users và items vào ứng dụng
app.include_router(users_router)
app.include_router(items_router)


# Sự kiện khởi động ứng dụng
@app.on_event("startup")
def startup_event():
    # Khởi tạo cấu hình logging
    logger.setup_logging()
    # Tạo bảng trong DB nếu chưa có (chỉ nên dùng trong môi trường phát triển)
    # Trong production, nên dùng Alembic migrations thay vì create_all.
    database.Base.metadata.create_all(bind=database.engine)
    print("Application startup: Database tables checked/created.")


# Sự kiện tắt ứng dụng
@app.on_event("shutdown")
def shutdown_event():
    print("Application shutdown.")

```

## File .\fastapi\app\model.py:
```python
# app/model
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    func,
    Numeric,
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(
        Integer, default=1
    )  # 1 = active, 0 = inactive (ví dụ trạng thái người dùng)

    # Quan hệ 1-n: một user có thể có nhiều item
    items = relationship("Item", back_populates="owner")

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Quan hệ ngược: mỗi item thuộc về một owner (user)
    owner = relationship("User", back_populates="items")

    def __repr__(self):
        return f"<Item(title='{self.title}', owner_id={self.owner_id})>"


# class Asset(Base):
#     __tablename__ = "asset"

#     id = Column(Integer, primary_key=True, index=True)
#     symbol = Column(String(10), unique=True, nullable=False, index=True)
#     name = Column(String(100), nullable=False)
#     description = Column(Text, nullable=True)


# class Portfolio(Base):
#     __tablename__ = "portfolio"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
#     name = Column(String(100), nullable=False)
#     description = Column(Text, nullable=True)
#     created_at = Column(DateTime, server_default=func.now())


# class PriceHistory(Base):
#     __tablename__ = "price_history"

#     id = Column(Integer, primary_key=True, index=True)
#     asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False, index=True)
#     date = Column(DateTime, nullable=False)
#     open_price = Column(Numeric(18, 8), nullable=True)
#     close_price = Column(Numeric(18, 8), nullable=True)
#     high_price = Column(Numeric(18, 8), nullable=True)
#     low_price = Column(Numeric(18, 8), nullable=True)
#     volume = Column(Numeric(18, 8), nullable=True)


# class Transaction(Base):
#     __tablename__ = "transaction"

#     id = Column(Integer, primary_key=True, index=True)
#     portfolio_id = Column(
#         Integer, ForeignKey("portfolio.id"), nullable=False, index=True
#     )
#     asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False, index=True)
#     transaction_type = Column(String(10), nullable=False)  # Ví dụ: 'mua', 'bán'
#     amount = Column(Numeric(18, 8), nullable=False)
#     price = Column(Numeric(18, 8), nullable=False)
#     fee = Column(Numeric(18, 8), nullable=True)
#     transaction_date = Column(DateTime, nullable=False, server_default=func.now())

```

## File .\fastapi\app\router.py:
```python
# app/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import model, database, auth

# Tạo các router cho user và item
users_router = APIRouter(prefix="/users")
items_router = APIRouter(prefix="/items")


# Endpoint: Đăng ký người dùng (Register)
@users_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    username: str, email: str, password: str, db: Session = Depends(database.get_db)
):
    # Kiểm tra username hoặc email đã tồn tại
    existing_user = (
        db.query(model.User)
        .filter((model.User.username == username) | (model.User.email == email))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )
    # Tạo đối tượng User mới
    hashed_pw = auth.get_password_hash(password)
    new_user = model.User(username=username, email=email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email}


# Endpoint: Đăng nhập (Login) – trả về JWT token
@users_router.post("/login")
def login(username: str, password: str, db: Session = Depends(database.get_db)):
    # Kiểm tra thông tin đăng nhập
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    # Tạo JWT token
    access_token = auth.create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Endpoint: Lấy thông tin người dùng hiện tại
@users_router.get("/me")
def read_current_user(current_user: model.User = Depends(auth.get_current_user)):
    # current_user được lấy qua dependency, ở đây ta chỉ trả về thông tin cơ bản
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }


# Endpoint: Lấy danh sách tất cả Item (có thể không yêu cầu đăng nhập)
@items_router.get("/", response_model=list[dict])
def get_items(db: Session = Depends(database.get_db)):
    items = db.query(model.Item).all()
    # Trả về danh sách item (chỉ bao gồm các trường cơ bản)
    return [
        {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "owner_id": item.owner_id,
        }
        for item in items
    ]


# Endpoint: Tạo Item mới (yêu cầu xác thực)
@items_router.post("/", status_code=status.HTTP_201_CREATED)
def create_item(
    title: str,
    description: str = None,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    # Tạo một item mới gắn với user hiện tại
    new_item = model.Item(
        title=title, description=description, owner_id=current_user.id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {
        "id": new_item.id,
        "title": new_item.title,
        "description": new_item.description,
        "owner_id": new_item.owner_id,
    }


# Endpoint: Xem chi tiết một Item theo ID
@items_router.get("/{item_id}")
def read_item(
    item_id: int,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    item = db.query(model.Item).filter(model.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    # Nếu muốn giới hạn, có thể kiểm tra quyền: chỉ cho phép chủ sở hữu xem, ở đây cho phép mọi user đã đăng nhập đều có thể xem
    return {
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "owner_id": item.owner_id,
    }


# Endpoint: Cập nhật Item (yêu cầu chủ sở hữu)
@items_router.put("/{item_id}")
def update_item(
    item_id: int,
    title: str = None,
    description: str = None,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    item = db.query(model.Item).filter(model.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this item"
        )
    # Cập nhật các trường được cung cấp
    if title is not None:
        item.title = title
    if description is not None:
        item.description = description
    db.commit()
    db.refresh(item)
    return {
        "message": "Item updated successfully",
        "item": {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "owner_id": item.owner_id,
        },
    }


# Endpoint: Xóa Item (yêu cầu chủ sở hữu)
@items_router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    item = db.query(model.Item).filter(model.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this item"
        )
    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}

```

## File .\fastapi\app\__init__.py:
```python

```

