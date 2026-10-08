from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.seed import seed_products
from app.routers import auth, products, cart, orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables and seed default products if needed
    init_db()
    seed_products()
    yield


app = FastAPI(
    title="Online Cart API",
    description="Production-ready REST API for authenticated online shopping cart application",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend service availability."""
    return {"status": "ok"}
