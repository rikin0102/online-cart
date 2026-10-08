from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CartItem, Product, User
from app.schemas import CartItemAdd, CartItemUpdate, CartResponse, CartItemResponse
from app.deps import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


def _calculate_user_cart(db: Session, user_id: int) -> CartResponse:
    """Helper to load user cart items, calculate Decimal line totals and grand total."""
    cart_items = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id)
        .join(Product, CartItem.product_id == Product.id)
        .order_by(CartItem.id.asc())
        .all()
    )

    response_items = []
    grand_total = Decimal("0.00")
    item_count = 0

    for item in cart_items:
        price = Decimal(str(item.product.price))
        line_total = price * Decimal(item.quantity)
        grand_total += line_total
        item_count += item.quantity

        response_items.append(
            CartItemResponse(
                product_id=item.product.id,
                name=item.product.name,
                price=price,
                quantity=item.quantity,
                line_total=line_total
            )
        )

    return CartResponse(
        items=response_items,
        grand_total=grand_total,
        item_count=item_count
    )


@router.get("", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all cart items, total quantity, and calculated grand total for the authenticated user."""
    return _calculate_user_cart(db, current_user.id)


@router.post("/items", response_model=CartResponse)
def add_to_cart(
    item_in: CartItemAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a product to the user's cart or increment its quantity up to max 99."""
    product = db.query(Product).filter(Product.id == item_in.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )

    cart_item = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id, CartItem.product_id == item_in.product_id)
        .first()
    )

    if cart_item:
        new_quantity = cart_item.quantity + item_in.quantity
        if new_quantity > 99:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity cannot exceed 99 units per item."
            )
        cart_item.quantity = new_quantity
    else:
        if item_in.quantity > 99:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity cannot exceed 99 units per item."
            )
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=item_in.product_id,
            quantity=item_in.quantity
        )
        db.add(cart_item)

    db.commit()
    return _calculate_user_cart(db, current_user.id)


@router.patch("/items/{product_id}", response_model=CartResponse)
def update_cart_item(
    product_id: int,
    item_in: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update exact quantity of a product in the authenticated user's cart."""
    if item_in.quantity < 1 or item_in.quantity > 99:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be between 1 and 99."
        )

    cart_item = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id, CartItem.product_id == product_id)
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in your cart."
        )

    cart_item.quantity = item_in.quantity
    db.commit()

    return _calculate_user_cart(db, current_user.id)


@router.delete("/items/{product_id}", response_model=CartResponse)
def remove_cart_item(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a product completely from the authenticated user's cart."""
    cart_item = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id, CartItem.product_id == product_id)
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in your cart."
        )

    db.delete(cart_item)
    db.commit()

    return _calculate_user_cart(db, current_user.id)
