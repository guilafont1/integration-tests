from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product
from app.schemas import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter()


@router.get("/products", response_model=list[ProductResponse])
def get_products(
    category: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    products_query = db.query(Product).filter(Product.active.is_(True))
    if category:
        products_query = products_query.filter(Product.category == category)
    if min_price is not None:
        products_query = products_query.filter(Product.price >= min_price)
    if max_price is not None:
        products_query = products_query.filter(Product.price <= max_price)
    products = products_query.offset(skip).limit(limit).all()
    return products


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product or not product.active:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    return product


@router.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_patch: ProductUpdate,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if not product or not product.active:
        raise HTTPException(status_code=404, detail="Produit introuvable")

    patch_data = product_patch.model_dump(exclude_unset=True)
    for field, value in patch_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product or not product.active:
        raise HTTPException(status_code=404, detail="Produit introuvable")

    product.active = False
    db.commit()
    return None
