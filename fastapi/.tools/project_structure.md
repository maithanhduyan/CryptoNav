# Cấu trúc Dự án như sau:

```
../fastapi
├── .devcontainer
│   └── devcontainer.json
├── .dockerignore
├── Dockerfile
├── alembic
│   ├── README
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── app
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── crud.py
│   ├── database.py
│   ├── logger.py
│   ├── main.py
│   ├── model.py
│   ├── router.py
│   └── schemas.py
├── requirements.txt
├── script
│   ├── setup.sh
│   └── start.sh
└── tests
    ├── __init__.py
    └── test_users.py
```

# Danh sách chi tiết các file:

## File ../fastapi/Dockerfile:
```
# Stage 1: Development
FROM ubuntu:24.04 AS development

# Cài đặt các gói cần thiết
RUN apt-get update && apt-get install -y curl python3 python3-pip

# Tạo user vscode
RUN useradd -ms /bin/bash vscode

# Thiết lập thư mục làm việc
WORKDIR /workstation

# Sao chép file requirements.txt
COPY ./fastapi/requirements.txt .

# Sao chép bash script
COPY script/start.sh /start.sh

# Chuyển quyền sở hữu thư mục cho user vscode
RUN chown -R vscode:vscode /workspace

# Chuyển sang user vscode
USER vscode

# Cài đặt uv bằng script và thêm vào PATH
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.bashrc

# Tạo virtual environment bằng uv
RUN /home/vscode/.local/bin/uv venv

# Cài đặt các gói python dependency = sử dụng uv
RUN /home/vscode/.local/bin/uv pip install -r requirements.txt

# Sử dụng cách gói python cài cũ
# RUN pip3 install -r requirements.txt

CMD ["bash", "setup.sh"]

# ------------------------------------------------------------------------------
FROM ubuntu:24.04 AS production

# Cập nhật và cài đặt Python3, pip, và các phụ thuộc cần thiết (ví dụ psycopg2)
RUN apt-get update && apt-get install -y python3 python3-pip build-essential libpq-dev

# Tạo thư mục làm việc
WORKDIR /app

# Sao chép file yêu cầu (để cài đặt thư viện Python)
COPY ./fastapi/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn của ứng dụng vào image
COPY app/ ./app
COPY alembic/ ./alembic
COPY alembic.ini .

# Sử dụng biến môi trường để xác định chế độ (dev hay prod)
ARG ENVIRONMENT=production
ENV ENVIRONMENT=${ENVIRONMENT}

# Mặc định, expose cổng 8000 (ứng dụng FastAPI sẽ chạy trên cổng này)
EXPOSE 8000

# Sao chép script khởi động (script này sẽ kiểm tra ENVIRONMENT để chạy tương ứng)
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Điểm khởi chạy container: chạy script start.sh
ENTRYPOINT ["/start.sh"]
```

## File ../fastapi/requirements.txt:
```
fastapi
uvicorn[standard]
sqlalchemy
alembic
PyJWT
python-json-logger
psycopg2-binary
alembic
bcrypt==4.3.0
pytest
```

## File ../fastapi/alembic/env.py:
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys, os

# Thêm đường dẫn thư mục gốc dự án vào PYTHONPATH
sys.path.append(os.getcwd())

from app.database import Base  # Import Base từ app.database
from app.config import DATABASE_URL

config = context.config
fileConfig(config.config_file_name)

# Gán metadata của các models để Alembic biết khi migrate
target_metadata = Base.metadata


def run_migrations_offline():
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = DATABASE_URL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

```

## File ../fastapi/app/auth.py:
```python
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

```

## File ../fastapi/app/config.py:
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

## File ../fastapi/app/crud.py:
```python
# app/crud.py
from sqlalchemy.orm import Session
from app import model

# --- CRUD for Asset ---


def get_asset(db: Session, asset_id: int):
    return db.query(model.Asset).filter(model.Asset.id == asset_id).first()


def get_assets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Asset).offset(skip).limit(limit).all()


def create_asset(db: Session, symbol: str, name: str, description: str = None):
    asset = model.Asset(symbol=symbol, name=name, description=description)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def update_asset(db: Session, asset_id: int, **kwargs):
    asset = db.query(model.Asset).filter(model.Asset.id == asset_id).first()
    for key, value in kwargs.items():
        setattr(asset, key, value)
    db.commit()
    db.refresh(asset)
    return asset


def delete_asset(db: Session, asset_id: int):
    asset = db.query(model.Asset).get(asset_id)
    db.delete(asset)
    db.commit()


# --- Portfolio CRUD ---
def get_portfolio(db: Session, portfolio_id: int):
    return db.query(model.Portfolio).get(portfolio_id)


def create_portfolio(db: Session, user_id: int, name: str):
    portfolio = model.Portfolio(user_id=user_id, name=name)
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio


def delete_portfolio(db: Session, portfolio_id: int):
    portfolio = db.query(model.Portfolio).get(portfolio_id)
    db.delete(portfolio)
    db.commit()


def update_portfolio(db: Session, portfolio_id: int, name: str):
    portfolio = db.query(model.Portfolio).get(portfolio_id)
    portfolio.name = name
    db.commit()
    db.refresh(portfolio)
    return portfolio


# --- CRUD for PriceHistory ---
def create_price_history(db: Session, asset_id: int, date, open_price, close_price):
    price_history = model.PriceHistory(
        asset_id=asset_id, date=date, open_price=open_price, close_price=close_price
    )
    db.add(price_history)
    db.commit()
    db.refresh(price_history)
    return price_history


def get_price_history_by_asset(db: Session, asset_id: int):
    return (
        db.query(model.PriceHistory)
        .filter(model.PriceHistory.asset_id == asset_id)
        .order_by(model.PriceHistory.date.desc())
        .all()
    )


# --- CRUD for Transaction ---
def create_transaction(
    db: Session,
    portfolio_id: int,
    asset_id: int,
    quantity: float,
    price: float,
    transaction_type: str,
    transaction_date,
):
    transaction = model.Transaction(
        portfolio_id=portfolio_id,
        asset_id=asset_id,
        transaction_date=transaction_date,
        quantity=quantity,
        price=price,
        type=transaction_type,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def get_transactions(db: Session, portfolio_id: int):
    return (
        db.query(model.Transaction)
        .filter(model.Transaction.portfolio_id == portfolio_id)
        .order_by(model.Transaction.transaction_date.desc())
        .all()
    )


def delete_transaction(db: Session, transaction_id: int):
    transaction = db.query(model.Transaction).get(transaction_id)
    db.delete(transaction)
    db.commit()

```

## File ../fastapi/app/database.py:
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

## File ../fastapi/app/logger.py:
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

## File ../fastapi/app/main.py:
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import (
    users_router,
    items_router,
    assets_router,
    portfolios_router,
    transactions_router,
)
from app import logger, config, database

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="CryptoNav API",
    description="API for managing cryptocurrency portfolios and tracking investments",
    version="1.0.0",
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tùy chỉnh theo yêu cầu cụ thể
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


# Gắn các router vào ứng dụng
app.include_router(users_router)
app.include_router(items_router)
app.include_router(assets_router)
app.include_router(portfolios_router)
app.include_router(transactions_router)


# Sự kiện khởi động ứng dụng
@app.on_event("startup")
def startup_event():
    # Khởi tạo logging
    logger.setup_logging()
    # Tạo bảng trong DB (dùng cho môi trường phát triển)
    database.Base.metadata.create_all(bind=database.engine)
    print("Application startup: Database tables checked/created.")


# Sự kiện tắt ứng dụng
@app.on_event("shutdown")
def shutdown_event():
    print("Application shutdown.")

```

## File ../fastapi/app/model.py:
```python
# app/model.py
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
    is_active = Column(Integer, default=1)

    items = relationship("Item", back_populates="owner")

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")

    def __repr__(self):
        return f"<Item(title='{self.title}', owner_id={self.owner_id})>"


class Asset(Base):
    __tablename__ = "asset"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Asset(symbol='{self.symbol}', name='{self.name}')>"


class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Portfolio(name='{self.name}', user_id={self.user_id})>"


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    open_price = Column(Numeric(18, 8), nullable=True)
    close_price = Column(Numeric(18, 8), nullable=True)
    high_price = Column(Numeric(18, 8), nullable=True)
    low_price = Column(Numeric(18, 8), nullable=True)

    def __repr__(self):
        return f"<PriceHistory(asset_id={self.asset_id}, date={self.date})>"


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(
        Integer, ForeignKey("portfolio.id"), nullable=False, index=True
    )
    asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False, index=True)
    quantity = Column(Numeric(18, 8), nullable=False)
    price = Column(Numeric(18, 8), nullable=False)
    transaction_type = Column(String(10), nullable=False)  # Ví dụ: 'mua', 'bán'
    transaction_date = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Transaction(type='{self.transaction_type}', portfolio_id={self.portfolio_id}, asset_id={self.asset_id})>"

```

## File ../fastapi/app/router.py:
```python
# app/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import model, database, auth, crud
from app.schemas import (
    AssetCreate,
    AssetResponse,
    ItemCreate,
    ItemResponse,
    PortfolioCreate,
    PortfolioResponse,
    TransactionCreate,
    TransactionResponse,
    UserBase,
    UserCreate,
    UserResponse,
)

# Tạo các router riêng biệt
users_router = APIRouter(prefix="/users", tags=["Users"])
items_router = APIRouter(prefix="/items")
assets_router = APIRouter(prefix="/assets")
portfolios_router = APIRouter(prefix="/portfolios")
transactions_router = APIRouter(prefix="/transactions")


# Dependency chung
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


# --- Item Endpoints ---
@items_router.get("/", response_model=List[ItemResponse])
def get_items(db: Session = Depends(get_db)):
    items = db.query(model.Item).all()
    return items


@items_router.post(
    "/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED
)
def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    new_item = model.Item(**item.dict(), owner_id=current_user.id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@items_router.get("/{item_id}", response_model=ItemResponse)
def read_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    item = db.query(model.Item).filter(model.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


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


# --- Asset Endpoints ---
@assets_router.get("/", response_model=List[AssetResponse])
def read_assets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_assets(db, skip=skip, limit=limit)


@assets_router.post("/", response_model=AssetResponse)
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    return crud.create_asset(db, **asset.dict())


@assets_router.get("/{asset_id}", response_model=AssetResponse)
def read_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = crud.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


# --- Portfolio Endpoints ---
@portfolios_router.post("/", response_model=PortfolioResponse)
def create_portfolio(portfolio: PortfolioCreate, db: Session = Depends(get_db)):
    new_portfolio = crud.create_portfolio(db, **portfolio.dict())
    return new_portfolio


@portfolios_router.get("/{portfolio_id}", response_model=PortfolioResponse)
def read_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = crud.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


@portfolios_router.get("/user/{user_id}", response_model=List[PortfolioResponse])
def read_user_portfolios(user_id: int, db: Session = Depends(get_db)):
    return crud.get_portfolios_by_user(db, user_id)


# --- Transaction Endpoints ---
@transactions_router.post("/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    new_transaction = crud.create_transaction(db, **transaction.dict())
    return new_transaction


@transactions_router.get("/{transaction_id}", response_model=TransactionResponse)
def read_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = crud.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@transactions_router.get(
    "/portfolio/{portfolio_id}", response_model=List[TransactionResponse]
)
def transactions_by_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    return crud.get_transactions_by_portfolio(db, portfolio_id)

```

## File ../fastapi/app/schemas.py:
```python
# app/schemas.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# --- User schemas ---


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


# --- Item schemas ---


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


# --- Asset schemas ---


class AssetBase(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=50)
    name: str
    description: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetResponse(AssetBase):
    id: int

    class Config:
        orm_mode = True


# --- Portfolio schemas ---


class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None


class PortfolioCreate(PortfolioBase):
    user_id: int


class PortfolioResponse(PortfolioBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# --- PriceHistory schemas ---


class PriceHistoryBase(BaseModel):
    asset_id: int
    date: datetime
    open_price: Optional[float] = None
    close_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None


class PriceHistoryCreate(PriceHistoryBase):
    pass


class PriceHistoryResponse(PriceHistoryBase):
    id: int

    class Config:
        orm_mode = True


# --- Transaction schemas ---


class TransactionBase(BaseModel):
    portfolio_id: int
    asset_id: int
    quantity: float
    price: float
    transaction_type: str = Field(..., min_length=1, max_length=10)  # "mua" or "bán"
    transaction_date: Optional[datetime] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int

    class Config:
        orm_mode = True

```

## File ../fastapi/app/__init__.py:
```python

```

## File ../fastapi/tests/test_users.py:
```python
# tests/test_users.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_user():
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass",
        },
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"


def test_login():
    client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass",
        },
    )
    response = client.post(
        "/users/login", data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

```

## File ../fastapi/tests/__init__.py:
```python

```

