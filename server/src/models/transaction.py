# src/models/transaction.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from src.database import Base
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
