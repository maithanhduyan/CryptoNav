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
