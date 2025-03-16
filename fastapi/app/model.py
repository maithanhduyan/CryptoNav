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
