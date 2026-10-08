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

# CORS middleware configuration - fully permissive for development, local networks, and production Vercel apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"^https?:\/\/.*",
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


# ============================================================================
# TEMPORARY DEVELOPMENT / TEST SMTP DIAGNOSTIC ENDPOINTS
# (Can be removed safely after testing SMTP connectivity on Render)
# ============================================================================
@app.get("/smtp-test", tags=["Diagnostics - Temporary"])
@app.get("/api/smtp-test", tags=["Diagnostics - Temporary"])
def smtp_diagnostic_test():
    """
    Temporary endpoint to diagnose SMTP connectivity directly from the server.
    - Checks environment variables (without leaking SMTP_PASSWORD)
    - Checks DNS resolution (IPv4 and IPv6)
    - Probes raw TCP connectivity on ports 587 and 465
    - Tests SMTP + STARTTLS handshake on port 587
    - Tests SMTP_SSL handshake on port 465
    - Tests SMTP authentication if credentials are provided
    - Does NOT send any real email
    """
    from app.email_service import test_smtp_connectivity
    return test_smtp_connectivity()

