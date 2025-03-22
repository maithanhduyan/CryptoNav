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
