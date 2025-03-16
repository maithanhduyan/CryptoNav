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
