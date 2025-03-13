from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.database import engine, Base
from src.routers import asset, auth, portfolio, price_history, transaction, user

# Create all database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="CryptoNav API",
    description="API for managing cryptocurrency portfolios and tracking investments",
    version="1.0.0",
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # Frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/api/users", tags=["Users"])
app.include_router(asset.router, prefix="/api/assets", tags=["Assets"])
app.include_router(portfolio.router, prefix="/api/portfolios", tags=["Portfolios"])
app.include_router(
    price_history.router, prefix="/api/price-history", tags=["Price History"]
)
app.include_router(
    transaction.router, prefix="/api/transactions", tags=["Transactions"]
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


from fastapi.responses import FileResponse


@app.get("/favicon.ico")
async def favicon():
    return FileResponse("./assets/favicon.ico")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
