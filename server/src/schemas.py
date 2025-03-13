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
