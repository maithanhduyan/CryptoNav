# src/services.py
from datetime import datetime
from sqlalchemy.orm import Session
from models.portfolio import Portfolio
from models.transaction import Transaction
from models.price_history import PriceHistory


def calculate_portfolio_value(db: Session, portfolio_id: int) -> float:
    """Tính giá trị hiện tại của một danh mục đầu tư dựa trên giao dịch và giá mới nhất."""
    transactions = (
        db.query(Transaction).filter(Transaction.portfolio_id == portfolio_id).all()
    )
    total_value = 0.0

    for transaction in transactions:
        latest_price = (
            db.query(PriceHistory)
            .filter(PriceHistory.asset_id == transaction.asset_id)
            .order_by(PriceHistory.date.desc())
            .first()
        )
        if latest_price and latest_price.close_price:
            amount = (
                transaction.amount
                if transaction.transaction_type == "mua"
                else -transaction.amount
            )
            total_value += amount * float(latest_price.close_price)

    return total_value


def get_asset_performance(
    db: Session, asset_id: int, start_date: datetime, end_date: datetime
) -> dict:
    """Tính hiệu suất của một tài sản trong khoảng thời gian."""
    price_history = (
        db.query(PriceHistory)
        .filter(PriceHistory.asset_id == asset_id)
        .filter(PriceHistory.date >= start_date)
        .filter(PriceHistory.date <= end_date)
        .order_by(PriceHistory.date)
        .all()
    )

    if not price_history:
        return {"error": "No price history available"}

    start_price = float(price_history[0].close_price or 0)
    end_price = float(price_history[-1].close_price or 0)
    performance = (
        ((end_price - start_price) / start_price) * 100 if start_price != 0 else 0
    )

    return {
        "asset_id": asset_id,
        "start_price": start_price,
        "end_price": end_price,
        "performance_percentage": performance,
    }
