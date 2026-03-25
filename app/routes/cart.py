from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CartItemCreate, CartResponse
from app.services.cart import add_item, get_or_create_cart

router = APIRouter()


@router.get("/cart/{user_id}", response_model=CartResponse)
def get_cart(user_id: int, db: Session = Depends(get_db)):
    cart = get_or_create_cart(db, user_id)
    return cart


@router.post("/cart/{user_id}/items", response_model=CartResponse)
def add_cart_item(
    user_id: int, item: CartItemCreate, db: Session = Depends(get_db)
):
    try:
        return add_item(db, user_id, item.product_id, item.quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
