# Cấu trúc Dự án như sau:

```
../server
├── .devcontainer
│   └── devcontainer.json
├── Dockerfile
├── cryptonav.db
└── src
    ├── auth.py
    ├── config.py
    ├── crud.py
    ├── database.py
    ├── main.py
    ├── models
    │   ├── asset.py
    │   ├── portfolio.py
    │   ├── price_history.py
    │   ├── transaction.py
    │   └── user.py
    ├── routers
    │   ├── __init__.py
    │   ├── asset.py
    │   ├── auth.py
    │   ├── portfolio.py
    │   ├── price_history.py
    │   ├── transaction.py
    │   └── user.py
    ├── schemas.py
    └── services.py
```

# Danh sách chi tiết các file:

## File ../server/src/auth.py:
```python
# src/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import bcrypt

from database import get_db
from models.user import User

SECRET_KEY = "your-secret-key"  # Nên đặt trong file config hoặc biến môi trường
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def hash_password(password: str) -> str:
    """Hash mật khẩu sử dụng bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Xác minh mật khẩu."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    """Tạo JWT token."""
    from datetime import datetime, timedelta

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Lấy thông tin người dùng hiện tại từ token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

```

## File ../server/src/config.py:
```python
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

```

## File ../server/src/crud.py:
```python
# src/crud.py
from sqlalchemy.orm import Session
from models.user import User
from models.asset import Asset
from models.portfolio import Portfolio
from models.transaction import Transaction
from models.price_history import PriceHistory


def create_item(db: Session, model_class, **kwargs):
    """Tạo một bản ghi mới trong database."""
    db_item = model_class(**kwargs)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_item(db: Session, model_class, item_id: int):
    """Lấy một bản ghi theo ID."""
    return db.query(model_class).filter(model_class.id == item_id).first()


def get_items(db: Session, model_class, skip: int = 0, limit: int = 100):
    """Lấy danh sách bản ghi với phân trang."""
    return db.query(model_class).offset(skip).limit(limit).all()


def update_item(db: Session, model_class, item_id: int, **kwargs):
    """Cập nhật một bản ghi."""
    db_item = get_item(db, model_class, item_id)
    if db_item:
        for key, value in kwargs.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item


def delete_item(db: Session, model_class, item_id: int):
    """Xóa một bản ghi."""
    db_item = get_item(db, model_class, item_id)
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item


# Ví dụ hàm cụ thể cho User
def create_user(db: Session, username: str, email: str, password: str):
    from src.auth import hash_password

    hashed_password = hash_password(password)
    return create_item(
        db, User, username=username, email=email, password=hashed_password
    )


def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()


# Có thể thêm các hàm khác cho Asset, Portfolio, Transaction, PriceHistory...

```

## File ../server/src/database.py:
```python
# src/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

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

```

## File ../server/src/main.py:
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import asset, auth, portfolio, price_history, transaction, user

# Create all database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="CryptoNav API",
    description="API for managing cryptocurrency portfolios and tracking investments",
    version="1.0.0",
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # Frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/api/users", tags=["Users"])
app.include_router(asset.router, prefix="/api/assets", tags=["Assets"])
app.include_router(portfolio.router, prefix="/api/portfolios", tags=["Portfolios"])
app.include_router(
    price_history.router, prefix="/api/price-history", tags=["Price History"]
)
app.include_router(
    transaction.router, prefix="/api/transactions", tags=["Transactions"]
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


from fastapi.responses import FileResponse


@app.get("/favicon.ico")
async def favicon():
    return FileResponse("./assets/favicon.ico")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

```

## File ../server/src/schemas.py:
```python
# src/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# User Schemas
class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# Asset Schemas
class AssetBase(BaseModel):
    symbol: str
    name: str
    description: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetResponse(AssetBase):
    id: int

    class Config:
        orm_mode = True


# Portfolio Schemas
class PortfolioBase(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioResponse(PortfolioBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# Transaction Schemas
class TransactionBase(BaseModel):
    portfolio_id: int
    asset_id: int
    transaction_type: str  # 'mua', 'bán', ...
    amount: float
    price: float
    fee: Optional[float] = None
    transaction_date: datetime


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int

    class Config:
        orm_mode = True


# PriceHistory Schemas
class PriceHistoryBase(BaseModel):
    asset_id: int
    date: datetime
    open_price: Optional[float] = None
    close_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    volume: Optional[float] = None


class PriceHistoryCreate(PriceHistoryBase):
    pass


class PriceHistoryResponse(PriceHistoryBase):
    id: int

    class Config:
        orm_mode = True


# Token Schema (dùng cho auth)
class Token(BaseModel):
    access_token: str
    token_type: str

```

## File ../server/src/services.py:
```python
# src/services.py
from datetime import datetime
from sqlalchemy.orm import Session
from models.portfolio import Portfolio
from models.transaction import Transaction
from models.price_history import PriceHistory


def calculate_portfolio_value(db: Session, portfolio_id: int) -> float:
    """Tính giá trị hiện tại của một danh mục đầu tư dựa trên giao dịch và giá mới nhất."""
    transactions = (
        db.query(Transaction).filter(Transaction.portfolio_id == portfolio_id).all()
    )
    total_value = 0.0

    for transaction in transactions:
        latest_price = (
            db.query(PriceHistory)
            .filter(PriceHistory.asset_id == transaction.asset_id)
            .order_by(PriceHistory.date.desc())
            .first()
        )
        if latest_price and latest_price.close_price:
            amount = (
                transaction.amount
                if transaction.transaction_type == "mua"
                else -transaction.amount
            )
            total_value += amount * float(latest_price.close_price)

    return total_value


def get_asset_performance(
    db: Session, asset_id: int, start_date: datetime, end_date: datetime
) -> dict:
    """Tính hiệu suất của một tài sản trong khoảng thời gian."""
    price_history = (
        db.query(PriceHistory)
        .filter(PriceHistory.asset_id == asset_id)
        .filter(PriceHistory.date >= start_date)
        .filter(PriceHistory.date <= end_date)
        .order_by(PriceHistory.date)
        .all()
    )

    if not price_history:
        return {"error": "No price history available"}

    start_price = float(price_history[0].close_price or 0)
    end_price = float(price_history[-1].close_price or 0)
    performance = (
        ((end_price - start_price) / start_price) * 100 if start_price != 0 else 0
    )

    return {
        "asset_id": asset_id,
        "start_price": start_price,
        "end_price": end_price,
        "performance_percentage": performance,
    }

```

## File ../server/src/models/asset.py:
```python
# src/models/asset.py
from sqlalchemy import Column, Integer, String, Text
from database import Base


class Asset(Base):
    __tablename__ = "asset"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

```

## File ../server/src/models/portfolio.py:
```python
# src/models/portfolio.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from database import Base


class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

```

## File ../server/src/models/price_history.py:
```python
# src/models/price_history.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric
from database import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    open_price = Column(Numeric(18, 8), nullable=True)
    close_price = Column(Numeric(18, 8), nullable=True)
    high_price = Column(Numeric(18, 8), nullable=True)
    low_price = Column(Numeric(18, 8), nullable=True)
    volume = Column(Numeric(18, 8), nullable=True)

```

## File ../server/src/models/transaction.py:
```python
# src/models/transaction.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from database import Base
from sqlalchemy.sql import func


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(
        Integer, ForeignKey("portfolio.id"), nullable=False, index=True
    )
    asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False, index=True)
    transaction_type = Column(String(10), nullable=False)  # Ví dụ: 'mua', 'bán'
    amount = Column(Numeric(18, 8), nullable=False)
    price = Column(Numeric(18, 8), nullable=False)
    fee = Column(Numeric(18, 8), nullable=True)
    transaction_date = Column(DateTime, nullable=False, server_default=func.now())

```

## File ../server/src/models/user.py:
```python
# src/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

```

## File ../server/src/routers/asset.py:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.asset import Asset
from typing import List
from schemas import AssetCreate, AssetResponse

router = APIRouter()


@router.post("/", response_model=AssetResponse)
async def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    db_asset = Asset(**asset.dict())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@router.get("/{asset_id}", response_model=AssetResponse)
async def read_asset(asset_id: int, db: Session = Depends(get_db)):
    db_asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if db_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return db_asset


@router.get("/", response_model=List[AssetResponse])
async def read_assets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    assets = db.query(Asset).offset(skip).limit(limit).all()
    return assets

```

## File ../server/src/routers/auth.py:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt

from database import get_db
from models.user import User
from schemas import UserCreate, Token

router = APIRouter()

SECRET_KEY = "your-secret-key"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    db_user = User(
        email=user.email,
        username=user.username,
        password=hashed_password.decode("utf-8"),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        return False
    return user

```

## File ../server/src/routers/portfolio.py:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.portfolio import Portfolio
from typing import List
from schemas import PortfolioCreate, PortfolioResponse

router = APIRouter()


@router.post("/", response_model=PortfolioResponse)
async def create_portfolio(portfolio: PortfolioCreate, db: Session = Depends(get_db)):
    db_portfolio = Portfolio(**portfolio.dict())
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def read_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    db_portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if db_portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return db_portfolio


@router.get("/user/{user_id}", response_model=List[PortfolioResponse])
async def read_user_portfolios(user_id: int, db: Session = Depends(get_db)):
    portfolios = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
    return portfolios

```

## File ../server/src/routers/price_history.py:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.price_history import PriceHistory
from typing import List
from schemas import PriceHistoryCreate, PriceHistoryResponse
from datetime import datetime

router = APIRouter()


@router.post("/", response_model=PriceHistoryResponse)
async def create_price_history(
    price: PriceHistoryCreate, db: Session = Depends(get_db)
):
    db_price = PriceHistory(**price.dict())
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price


@router.get("/asset/{asset_id}", response_model=List[PriceHistoryResponse])
async def read_asset_price_history(
    asset_id: int,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
):
    query = db.query(PriceHistory).filter(PriceHistory.asset_id == asset_id)
    if start_date:
        query = query.filter(PriceHistory.date >= start_date)
    if end_date:
        query = query.filter(PriceHistory.date <= end_date)
    return query.all()

```

## File ../server/src/routers/transaction.py:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.transaction import Transaction
from typing import List
from schemas import TransactionCreate, TransactionResponse

router = APIRouter()


@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate, db: Session = Depends(get_db)
):
    db_transaction = Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get("/portfolio/{portfolio_id}", response_model=List[TransactionResponse])
async def read_portfolio_transactions(portfolio_id: int, db: Session = Depends(get_db)):
    transactions = (
        db.query(Transaction).filter(Transaction.portfolio_id == portfolio_id).all()
    )
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def read_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = (
        db.query(Transaction).filter(Transaction.id == transaction_id).first()
    )
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

```

## File ../server/src/routers/user.py:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from typing import List
from schemas import UserResponse
from crud import create_user, get_item, get_items
from auth import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

```

## File ../server/src/routers/__init__.py:
```python
from . import auth, user, asset, portfolio, price_history, transaction

__all__ = ["auth", "user", "asset", "portfolio", "price_history", "transaction"]

```

