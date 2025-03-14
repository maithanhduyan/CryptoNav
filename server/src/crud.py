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
