from fastapi import APIRouter

router = APIRouter()


@router.get("/coupons")
def get_coupons():
    return []
