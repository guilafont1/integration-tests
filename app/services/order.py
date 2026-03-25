from sqlalchemy.orm import Session

from app.models import Cart, Coupon, Order, OrderItem, Product
from app.services.pricing import calculer_total


def _get_coupon(db: Session, code: str | None) -> Coupon | None:
    if not code:
        return None
    return db.query(Coupon).filter(Coupon.code == code).first()


def create_order_from_cart(
    db: Session, user_id: int, coupon_code: str | None = None
) -> Order:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart or not cart.items:
        raise ValueError("Panier vide")

    coupon = _get_coupon(db, coupon_code)
    produits = [
        (db.get(Product, i.product_id), i.quantity)
        for i in cart.items
    ]

    total_ht = sum(p.price * q for p, q in produits)
    total_ttc = calculer_total(produits, coupon=coupon)

    order = Order(
        user_id=user_id,
        total_ht=round(total_ht, 2),
        total_ttc=total_ttc,
        coupon_code=coupon.code if coupon else None,
        status="created",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    for p, q in produits:
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=p.id,
                quantity=q,
                unit_price=p.price,
            )
        )

    db.commit()
    db.refresh(order)
    return order
