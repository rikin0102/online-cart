from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, User
from app.schemas import ProductResponse
from app.deps import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[ProductResponse])
def get_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all available catalog products from the database for authenticated users."""
    products = db.query(Product).order_by(Product.id.asc()).all()
    return products
