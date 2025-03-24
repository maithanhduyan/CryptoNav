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
RUN apt update && apt install -y curl git && \
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
  apt install -y nodejs \
  python3 python3-pip


# Tạo user vscode
RUN useradd -ms /bin/bash vscode
# Chuyển sang user vscode
USER vscode

# Cài đặt uv bằng script và thêm vào PATH
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.bashrc

# Thiết lập thư mục làm việc
WORKDIR /workspace
# Chuyển quyền sở hữu thư mục cho user vscode
RUN chown -R vscode:vscode /workspace

# Tạo virtual environment bằng uv
RUN /home/vscode/.local/bin/uv venv /home/vscode/pylinux --python 3.12
# Thêm virtual environment vào PATH
ENV PATH="/home/vscode/pylinux/bin:$PATH"

# Sao chép file requirements.txt
COPY ./fastapi/requirements.txt .


# Cài đặt các gói python dependency = sử dụng uv
RUN /home/vscode/.local/bin/uv pip install -r requirements.txt

# Sao chép bash script
COPY ./fastapi/script/setup.sh /setup.sh
CMD ["bash", "setup.sh"]

# ------------------------------------------------------------------------------
# PRODUCTION Dockerfile
# ------------------------------------------------------------------------------
FROM ubuntu:24.04 AS production

# 1. Cài đặt gói cần thiết: python3, pip, curl
RUN apt-get update && apt-get install -y \
  python3 \
  python3-pip \
  curl \
  && rm -rf /var/lib/apt/lists/*

# 2. Thiết lập PATH để có thể gọi uv từ ~/.local/bin
ENV PATH="/root/.local/bin:$PATH"

# 3. Cài đặt uv (script cài đặt từ astral.sh)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# 4. Tạo thư mục làm việc cho app
WORKDIR /app

# 5. Sao chép file yêu cầu Python (requirements.txt) và cài đặt trong venv
COPY requirements.txt ./

# Tạo venv ở /root/venv (hoặc tuỳ ý) và cài đặt dependencies bằng uv pip
RUN uv venv /home/venv 
# Thêm virtual environment vào PATH
ENV PATH="/home/venv/bin:$PATH"
# Cài đặt các gói python dependency = sử dụng uv
RUN uv pip install -r requirements.txt

# 6.Sao chép mã nguồn của ứng dụng vào image
COPY app/ ./app
COPY alembic/ ./alembic
COPY alembic.ini .

# 7.Sử dụng biến môi trường để xác định chế độ (dev hay prod)
ARG ENVIRONMENT=production
ENV ENVIRONMENT=${ENVIRONMENT}

# 8. Copy script khởi động & cấp quyền thực thi
COPY ./script/start.sh /start.sh
RUN chmod +x /start.sh

# 9. Mặc định expose cổng 8000 (FastAPI)
EXPOSE 8000

# 10. Điểm khởi chạy container: chạy script start.sh
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
passlib
pytest
pydantic[email]
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
from app import config, model, database
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
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
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Băm mật khẩu (hash password) để lưu vào DB."""
    return pwd_context.hash(password)


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

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


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
    PortfolioCreate,
    PortfolioBase,
    PortfolioResponse,
    TransactionCreate,
    TransactionResponse,
    UserBase,
    UserCreate,
    UserResponse,
    PriceHistoryCreate,
    PriceHistoryResponse
)

# Tạo các router riêng biệt
users_router = APIRouter(prefix="/users", tags=["Users"])
assets_router = APIRouter(prefix="/assets", tags=["Assets"])
portfolios_router = APIRouter(prefix="/portfolios", tags=["Portfolios"])
transactions_router = APIRouter(prefix="/transactions", tags=["Transactions"])

# Dependency chung
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- User Endpoints ---

# Endpoint: Đăng ký người dùng (Register) - Không cần token
@users_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(model.User)
        .filter((model.User.username == user.username) | (model.User.email == user.email))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )
    hashed_pw = auth.get_password_hash(user.password)
    new_user = model.User(username=user.username, email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Endpoint: Đăng nhập (Login) - Không cần token
@users_router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = auth.create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint: Lấy thông tin người dùng hiện tại - Yêu cầu token
@users_router.get("/me", response_model=UserResponse)
def read_current_user(current_user: model.User = Depends(auth.get_current_user)):
    return current_user

# Endpoint: Lấy danh sách tất cả người dùng - Yêu cầu token
@users_router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    users = db.query(model.User).offset(skip).limit(limit).all()
    return users

# Endpoint: Lấy thông tin người dùng theo ID - Yêu cầu token
@users_router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    user = db.query(model.User).filter(model.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Endpoint: Cập nhật thông tin người dùng - Yêu cầu token
@users_router.put("/me", response_model=UserResponse)
def update_user(
    email: str = None,
    password: str = None,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    if email:
        current_user.email = email
    if password:
        current_user.hashed_password = auth.get_password_hash(password)
    db.commit()
    db.refresh(current_user)
    return current_user

# Endpoint: Xóa tài khoản người dùng - Yêu cầu token
@users_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted successfully"}

# --- Asset Endpoints ---

# Endpoint: Lấy danh sách tất cả tài sản - Yêu cầu token
@assets_router.get("/", response_model=List[AssetResponse])
def read_assets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    return crud.get_assets(db, skip=skip, limit=limit)

# Endpoint: Tạo tài sản mới - Yêu cầu token
@assets_router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(
    asset: AssetCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    return crud.create_asset(db, **asset.dict())

# Endpoint: Lấy thông tin tài sản theo ID - Yêu cầu token
@assets_router.get("/{asset_id}", response_model=AssetResponse)
def read_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    asset = crud.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

# Endpoint: Cập nhật thông tin tài sản - Yêu cầu token
@assets_router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int,
    asset: AssetCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    updated_asset = crud.update_asset(db, asset_id, **asset.dict())
    if not updated_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return updated_asset

# Endpoint: Xóa tài sản - Yêu cầu token
@assets_router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    asset = crud.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    crud.delete_asset(db, asset_id)
    return {"message": "Asset deleted successfully"}

# --- Portfolio Endpoints ---

# Endpoint: Tạo danh mục đầu tư mới - Yêu cầu token
@portfolios_router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    portfolio_data = portfolio.dict()
    portfolio_data["user_id"] = current_user.id
    new_portfolio = crud.create_portfolio(db, **portfolio_data)
    return new_portfolio

# Endpoint: Lấy thông tin danh mục đầu tư theo ID - Yêu cầu token
@portfolios_router.get("/{portfolio_id}", response_model=PortfolioResponse)
def read_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    portfolio = crud.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this portfolio")
    return portfolio

# Endpoint: Lấy danh sách danh mục đầu tư của người dùng hiện tại - Yêu cầu token
@portfolios_router.get("/my-portfolios", response_model=List[PortfolioResponse])
def read_user_portfolios(
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    portfolios = db.query(model.Portfolio).filter(model.Portfolio.user_id == current_user.id).all()
    return portfolios

# Endpoint: Cập nhật danh mục đầu tư - Yêu cầu token và quyền sở hữu
@portfolios_router.put("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(
    portfolio_id: int,
    portfolio: PortfolioBase,  # Nhận dữ liệu từ body thay vì query
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    existing_portfolio = crud.get_portfolio(db, portfolio_id)
    if not existing_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if existing_portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this portfolio")

    updated_portfolio = crud.update_portfolio(db, portfolio_id, name=portfolio.name)
    if portfolio.description is not None:
        updated_portfolio.description = portfolio.description
        db.commit()
        db.refresh(updated_portfolio)
    return updated_portfolio

# Endpoint: Xóa danh mục đầu tư - Yêu cầu token và quyền sở hữu
@portfolios_router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    portfolio = crud.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this portfolio")
    crud.delete_portfolio(db, portfolio_id)
    return {"message": "Portfolio deleted successfully"}

# --- Transaction Endpoints ---

# Endpoint: Tạo giao dịch mới - Yêu cầu token và quyền sở hữu danh mục
@transactions_router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    portfolio = crud.get_portfolio(db, transaction.portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add transaction to this portfolio")
    new_transaction = crud.create_transaction(db, **transaction.dict())
    return new_transaction

# Endpoint: Lấy thông tin giao dịch theo ID - Yêu cầu token và quyền sở hữu danh mục
@transactions_router.get("/{transaction_id}", response_model=TransactionResponse)
def read_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    transaction = db.query(model.Transaction).filter(model.Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    portfolio = crud.get_portfolio(db, transaction.portfolio_id)
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this transaction")
    return transaction

# Endpoint: Lấy danh sách giao dịch theo danh mục đầu tư - Yêu cầu token và quyền sở hữu
@transactions_router.get("/portfolio/{portfolio_id}", response_model=List[TransactionResponse])
def transactions_by_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    portfolio = crud.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view transactions of this portfolio")
    return crud.get_transactions(db, portfolio_id)

# Endpoint: Cập nhật giao dịch - Yêu cầu token và quyền sở hữu danh mục
# Endpoint: Cập nhật giao dịch - Nhận dữ liệu từ body
@transactions_router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    existing_transaction = db.query(model.Transaction).filter(model.Transaction.id == transaction_id).first()
    if not existing_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    portfolio = crud.get_portfolio(db, existing_transaction.portfolio_id)
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this transaction")

    for key, value in transaction.dict().items():
        setattr(existing_transaction, key, value)
    db.commit()
    db.refresh(existing_transaction)
    return existing_transaction

# Endpoint: Xóa giao dịch - Yêu cầu token và quyền sở hữu danh mục
@transactions_router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    transaction = db.query(model.Transaction).filter(model.Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    portfolio = crud.get_portfolio(db, transaction.portfolio_id)
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this transaction")
    crud.delete_transaction(db, transaction_id)
    return {"message": "Transaction deleted successfully"}


# Endpoint: Lấy lịch sử giá của một asset
@assets_router.get("/{asset_id}/price-history", response_model=List[PriceHistoryResponse])
def read_price_history(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    asset = crud.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    price_history = crud.get_price_history_by_asset(db, asset_id)
    return price_history

# Endpoint: Tạo lịch sử giá mới cho asset
@assets_router.post("/{asset_id}/price-history", response_model=PriceHistoryResponse, status_code=status.HTTP_201_CREATED)
def create_price_history(
    asset_id: int,
    price_history: PriceHistoryCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    # Kiểm tra asset tồn tại
    asset = crud.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Tạo bản ghi mới
    new_price_history = crud.create_price_history(
        db=db,
        asset_id=asset_id,
        date=price_history.date,
        open_price=price_history.open_price,
        close_price=price_history.close_price,
        high_price=price_history.high_price,
        low_price=price_history.low_price
    )
    return new_price_history

# Endpoint: Cập nhật lịch sử giá cho asset
@assets_router.put("/{asset_id}/price-history/{price_history_id}", response_model=PriceHistoryResponse)
def update_price_history(
    asset_id: int,
    price_history_id: int,
    price_history: PriceHistoryCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    # Kiểm tra asset tồn tại
    asset = crud.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Kiểm tra price_history tồn tại
    existing_price_history = db.query(model.PriceHistory).filter(
        model.PriceHistory.id == price_history_id,
        model.PriceHistory.asset_id == asset_id
    ).first()
    if not existing_price_history:
        raise HTTPException(status_code=404, detail="Price history not found")

    # Cập nhật dữ liệu
    for key, value in price_history.dict().items():
        setattr(existing_price_history, key, value)
    db.commit()
    db.refresh(existing_price_history)
    return existing_price_history

# Endpoint: Xóa lịch sử giá cho asset
@assets_router.delete("/{asset_id}/price-history/{price_history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_price_history(
    asset_id: int,
    price_history_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    # Kiểm tra asset tồn tại
    asset = crud.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Kiểm tra price_history tồn tại
    price_history = db.query(model.PriceHistory).filter(
        model.PriceHistory.id == price_history_id,
        model.PriceHistory.asset_id == asset_id
    ).first()
    if not price_history:
        raise HTTPException(status_code=404, detail="Price history not found")

    # Xóa bản ghi
    db.delete(price_history)
    db.commit()
    return {"message": "Price history deleted successfully"}
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

