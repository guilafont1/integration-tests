from fastapi import APIRouter

router = APIRouter()


@router.get("/cart")
def get_cart():
    return {}
