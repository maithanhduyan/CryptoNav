# app/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import model, database, auth, crud
from app.schemas import (
    AssetCreate,
    AssetResponse,
    ItemCreate,
    ItemResponse,
    PortfolioCreate,
    PortfolioResponse,
    TransactionCreate,
    TransactionResponse,
    UserBase,
    UserCreate,
    UserResponse,
)

# Tạo các router riêng biệt
users_router = APIRouter(prefix="/users", tags=["Users"])
items_router = APIRouter(prefix="/items")
assets_router = APIRouter(prefix="/assets")
portfolios_router = APIRouter(prefix="/portfolios")
transactions_router = APIRouter(prefix="/transactions")


# Dependency chung
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Endpoint: Đăng ký người dùng (Register)
@users_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    username: str, email: str, password: str, db: Session = Depends(database.get_db)
):
    # Kiểm tra username hoặc email đã tồn tại
    existing_user = (
        db.query(model.User)
        .filter((model.User.username == username) | (model.User.email == email))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )
    # Tạo đối tượng User mới
    hashed_pw = auth.get_password_hash(password)
    new_user = model.User(username=username, email=email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email}


# Endpoint: Đăng nhập (Login) – trả về JWT token
@users_router.post("/login")
def login(username: str, password: str, db: Session = Depends(database.get_db)):
    # Kiểm tra thông tin đăng nhập
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    # Tạo JWT token
    access_token = auth.create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Endpoint: Lấy thông tin người dùng hiện tại
@users_router.get("/me")
def read_current_user(current_user: model.User = Depends(auth.get_current_user)):
    # current_user được lấy qua dependency, ở đây ta chỉ trả về thông tin cơ bản
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }


# --- Item Endpoints ---
@items_router.get("/", response_model=List[ItemResponse])
def get_items(db: Session = Depends(get_db)):
    items = db.query(model.Item).all()
    return items


@items_router.post(
    "/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED
)
def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    new_item = model.Item(**item.dict(), owner_id=current_user.id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@items_router.get("/{item_id}", response_model=ItemResponse)
def read_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    item = db.query(model.Item).filter(model.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# Endpoint: Cập nhật Item (yêu cầu chủ sở hữu)
@items_router.put("/{item_id}")
def update_item(
    item_id: int,
    title: str = None,
    description: str = None,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    item = db.query(model.Item).filter(model.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this item"
        )
    # Cập nhật các trường được cung cấp
    if title is not None:
        item.title = title
    if description is not None:
        item.description = description
    db.commit()
    db.refresh(item)
    return {
        "message": "Item updated successfully",
        "item": {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "owner_id": item.owner_id,
        },
    }


# Endpoint: Xóa Item (yêu cầu chủ sở hữu)
@items_router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    item = db.query(model.Item).filter(model.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this item"
        )
    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}


# --- Asset Endpoints ---
@assets_router.get("/", response_model=List[AssetResponse])
def read_assets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_assets(db, skip=skip, limit=limit)


@assets_router.post("/", response_model=AssetResponse)
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    return crud.create_asset(db, **asset.dict())


@assets_router.get("/{asset_id}", response_model=AssetResponse)
def read_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = crud.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


# --- Portfolio Endpoints ---
@portfolios_router.post("/", response_model=PortfolioResponse)
def create_portfolio(portfolio: PortfolioCreate, db: Session = Depends(get_db)):
    new_portfolio = crud.create_portfolio(db, **portfolio.dict())
    return new_portfolio


@portfolios_router.get("/{portfolio_id}", response_model=PortfolioResponse)
def read_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = crud.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


@portfolios_router.get("/user/{user_id}", response_model=List[PortfolioResponse])
def read_user_portfolios(user_id: int, db: Session = Depends(get_db)):
    return crud.get_portfolios_by_user(db, user_id)


# --- Transaction Endpoints ---
@transactions_router.post("/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    new_transaction = crud.create_transaction(db, **transaction.dict())
    return new_transaction


@transactions_router.get("/{transaction_id}", response_model=TransactionResponse)
def read_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = crud.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@transactions_router.get(
    "/portfolio/{portfolio_id}", response_model=List[TransactionResponse]
)
def transactions_by_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    return crud.get_transactions_by_portfolio(db, portfolio_id)
