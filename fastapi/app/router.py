# app/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import model, database, auth, crud
from app.schemas import (
    AssetCreate,
    AssetResponse,
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
assets_router = APIRouter(prefix="/assets", tags=["Assets"])
portfolios_router = APIRouter(prefix="/portfolios", tags=["Portfolios"])
transactions_router = APIRouter(prefix="/transactions", tags=["Transactions"])

# Dependency chung
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- User Endpoints ---

# Endpoint: Đăng ký người dùng (Register)
@users_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    # Kiểm tra username hoặc email đã tồn tại
    existing_user = (
        db.query(model.User)
        .filter((model.User.username == user.username) | (model.User.email == user.email))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )
    # Tạo đối tượng User mới
    hashed_pw = auth.get_password_hash(user.password)
    new_user = model.User(username=user.username, email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Endpoint: Đăng nhập (Login) – trả về JWT token
@users_router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    # Kiểm tra thông tin đăng nhập
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    # Tạo JWT token
    access_token = auth.create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint: Lấy thông tin người dùng hiện tại
@users_router.get("/me", response_model=UserResponse)
def read_current_user(current_user: model.User = Depends(auth.get_current_user)):
    return current_user

# Endpoint: Lấy danh sách tất cả người dùng (chỉ để test, không khuyến khích trong production)
@users_router.get("/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(model.User).offset(skip).limit(limit).all()
    return users

# Endpoint: Lấy thông tin người dùng theo ID
@users_router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Endpoint: Cập nhật thông tin người dùng (chỉ người dùng hiện tại)
@users_router.put("/me", response_model=UserResponse)
def update_user(
    email: str = None,
    password: str = None,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    if email:
        current_user.email = email
    if password:
        current_user.hashed_password = auth.get_password_hash(password)
    db.commit()
    db.refresh(current_user)
    return current_user

# Endpoint: Xóa tài khoản người dùng (chỉ người dùng hiện tại)
@users_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted successfully"}

# --- Asset Endpoints ---

# Endpoint: Lấy danh sách tất cả tài sản
@assets_router.get("/", response_model=List[AssetResponse])
def read_assets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_assets(db, skip=skip, limit=limit)

# Endpoint: Tạo tài sản mới
@assets_router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    return crud.create_asset(db, **asset.dict())

# Endpoint: Lấy thông tin tài sản theo ID
@assets_router.get("/{asset_id}", response_model=AssetResponse)
def read_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = crud.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

# Endpoint: Cập nhật thông tin tài sản
@assets_router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int,
    asset: AssetCreate,
    db: Session = Depends(get_db),
):
    updated_asset = crud.update_asset(db, asset_id, **asset.dict())
    if not updated_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return updated_asset

# Endpoint: Xóa tài sản
@assets_router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = crud.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    crud.delete_asset(db, asset_id)
    return {"message": "Asset deleted successfully"}

# --- Portfolio Endpoints ---

# Endpoint: Tạo danh mục đầu tư mới
@portfolios_router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    # Gán user_id từ người dùng hiện tại
    portfolio_data = portfolio.dict()
    portfolio_data["user_id"] = current_user.id
    new_portfolio = crud.create_portfolio(db, **portfolio_data)
    return new_portfolio

# Endpoint: Lấy thông tin danh mục đầu tư theo ID
@portfolios_router.get("/{portfolio_id}", response_model=PortfolioResponse)
def read_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = crud.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

# Endpoint: Lấy danh sách danh mục đầu tư của người dùng hiện tại
@portfolios_router.get("/my-portfolios", response_model=List[PortfolioResponse])
def read_user_portfolios(
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    portfolios = db.query(model.Portfolio).filter(model.Portfolio.user_id == current_user.id).all()
    return portfolios

# Endpoint: Cập nhật danh mục đầu tư (chỉ chủ sở hữu)
@portfolios_router.put("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(
    portfolio_id: int,
    name: str,
    description: str = None,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    portfolio = crud.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this portfolio")
    updated_portfolio = crud.update_portfolio(db, portfolio_id, name=name)
    if description:
        updated_portfolio.description = description
        db.commit()
        db.refresh(updated_portfolio)
    return updated_portfolio

# Endpoint: Xóa danh mục đầu tư (chỉ chủ sở hữu)
@portfolios_router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    portfolio = crud.get_portfolio(db, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this portfolio")
    crud.delete_portfolio(db, portfolio_id)
    return {"message": "Portfolio deleted successfully"}

# --- Transaction Endpoints ---

# Endpoint: Tạo giao dịch mới
@transactions_router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    portfolio = crud.get_portfolio(db, transaction.portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add transaction to this portfolio")
    new_transaction = crud.create_transaction(db, **transaction.dict())
    return new_transaction

# Endpoint: Lấy thông tin giao dịch theo ID
@transactions_router.get("/{transaction_id}", response_model=TransactionResponse)
def read_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(model.Transaction).filter(model.Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

# Endpoint: Lấy danh sách giao dịch theo danh mục đầu tư
@transactions_router.get("/portfolio/{portfolio_id}", response_model=List[TransactionResponse])
def transactions_by_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    return crud.get_transactions(db, portfolio_id)

# Endpoint: Cập nhật giao dịch (chỉ chủ sở hữu danh mục)
@transactions_router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    existing_transaction = db.query(model.Transaction).filter(model.Transaction.id == transaction_id).first()
    if not existing_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    portfolio = crud.get_portfolio(db, existing_transaction.portfolio_id)
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this transaction")

    for key, value in transaction.dict().items():
        setattr(existing_transaction, key, value)
    db.commit()
    db.refresh(existing_transaction)
    return existing_transaction

# Endpoint: Xóa giao dịch (chỉ chủ sở hữu danh mục)
@transactions_router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    transaction = db.query(model.Transaction).filter(model.Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    portfolio = crud.get_portfolio(db, transaction.portfolio_id)
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this transaction")
    crud.delete_transaction(db, transaction_id)
    return {"message": "Transaction deleted successfully"}