# src/models/price_history.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric
from src.database import Base


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
