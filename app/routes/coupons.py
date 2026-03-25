from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Coupon
from app.schemas import CouponCreate, CouponResponse

router = APIRouter()


@router.get("/coupons", response_model=list[CouponResponse])
def get_coupons(db: Session = Depends(get_db)):
    return db.query(Coupon).all()


@router.post("/coupons", response_model=CouponResponse)
def create_coupon(coupon: CouponCreate, db: Session = Depends(get_db)):
    existing = db.query(Coupon).filter(Coupon.code == coupon.code).first()
    if existing:
        raise HTTPException(status_code=409, detail="Coupon déjà existant")

    db_coupon = Coupon(**coupon.model_dump())
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon
