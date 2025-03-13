from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.transaction import Transaction
from typing import List
from src.schemas import TransactionCreate, TransactionResponse

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
