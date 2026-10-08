from decimal import Decimal
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CartItem, Product, Order, OrderItem, User
from app.schemas import OrderResponse
from app.deps import get_current_user
from app.email_service import send_order_summary_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/submit", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def submit_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit and place an order atomically from the user's cart items:
    1. Verify non-empty cart
    2. Read current product names and prices from DB
    3. Calculate snapshot line totals and grand total using Decimal
    4. Save Order and OrderItems records atomically and clear cart
    5. Attempt SMTP email dispatch; update email_status accordingly
    """
    # 1 & 2: Load user's cart items with product relationship
    cart_items = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id)
        .join(Product, CartItem.product_id == Product.id)
        .all()
    )

    # 3: Check cart is not empty
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot place order. Your cart is empty."
        )

    try:
        grand_total = Decimal("0.00")
        order_items_to_create = []

        # 4, 5, 6: Calculate totals & build snapshot order items
        for cart_item in cart_items:
            product = cart_item.product
            price = Decimal(str(product.price))
            quantity = cart_item.quantity
            line_total = price * Decimal(quantity)
            grand_total += line_total

            order_items_to_create.append({
                "product_name": product.name,
                "price": price,
                "quantity": quantity,
                "line_total": line_total
            })

        # 7: Create Order
        new_order = Order(
            user_id=current_user.id,
            grand_total=grand_total,
            email_status="failed"  # Default before sending
        )
        db.add(new_order)
        db.flush()  # Flush to get new_order.id for OrderItem foreign keys

        # 8, 9, 10: Create OrderItems with snapshots
        db_order_items = []
        for item_data in order_items_to_create:
            order_item = OrderItem(
                order_id=new_order.id,
                product_name=item_data["product_name"],
                price=item_data["price"],
                quantity=item_data["quantity"],
                line_total=item_data["line_total"]
            )
            db.add(order_item)
            db_order_items.append(order_item)

        # 11: Clear user's cart
        for cart_item in cart_items:
            db.delete(cart_item)

        # 12: Commit transaction
        db.commit()
        db.refresh(new_order)

    except Exception as exc:
        db.rollback()
        logger.error(f"Error executing atomic order placement for user {current_user.id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your order. Please try again."
        )

    # 13 & 14: Attempt to send email without crashing the order
    email_success = send_order_summary_email(
        recipient_email=current_user.email,
        recipient_name=current_user.name,
        order_id=new_order.id,
        order_items=db_order_items,
        grand_total=grand_total
    )

    if email_success:
        try:
            new_order.email_status = "sent"
            db.commit()
            db.refresh(new_order)
        except Exception as e:
            logger.error(f"Failed to update email status for Order #{new_order.id}: {e}")

    # 15: Return order summary
    return new_order
