from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import OrderCreate, OrderResponse
from app.services.order import create_order_from_cart

router = APIRouter()


@router.post("/orders", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    try:
        return create_order_from_cart(db, order.user_id, order.coupon_code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
