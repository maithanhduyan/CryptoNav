# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import (
    users_router,
    items_router,
    assets_router,
    portfolios_router,
    transactions_router,
)
from app import logger, config, database

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="CryptoNav API",
    description="API for managing cryptocurrency portfolios and tracking investments",
    version="1.0.0",
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tùy chỉnh theo yêu cầu cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to CryptoNav API",
        "documentation": "/docs",
        "redoc": "/redoc",
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


# Gắn các router vào ứng dụng
app.include_router(users_router)
app.include_router(items_router)
app.include_router(assets_router)
app.include_router(portfolios_router)
app.include_router(transactions_router)


# Sự kiện khởi động ứng dụng
@app.on_event("startup")
def startup_event():
    # Khởi tạo logging
    logger.setup_logging()
    # Tạo bảng trong DB (dùng cho môi trường phát triển)
    database.Base.metadata.create_all(bind=database.engine)
    print("Application startup: Database tables checked/created.")


# Sự kiện tắt ứng dụng
@app.on_event("shutdown")
def shutdown_event():
    print("Application shutdown.")
