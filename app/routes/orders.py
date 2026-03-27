from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order
from app.schemas import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services.order import create_order_from_cart, update_order_status

router = APIRouter()


@router.post(
    "/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    try:
        return create_order_from_cart(db, order.user_id, order.coupon_code)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    return order


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def patch_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        return update_order_status(db, order_id, status_update.status)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
