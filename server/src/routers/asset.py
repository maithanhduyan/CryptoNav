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
