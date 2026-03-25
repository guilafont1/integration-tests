from sqlalchemy.orm import Session

from app.models import Cart, CartItem, Product
from app.services.stock import reserver_stock


def get_or_create_cart(db: Session, user_id: int) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if cart:
        return cart

    cart = Cart(user_id=user_id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart


def add_item(db: Session, user_id: int, product_id: int, quantity: int) -> Cart:
    if quantity <= 0:
        raise ValueError(f"Quantité invalide : {quantity}")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ValueError(f"Produit introuvable : {product_id}")

    reserver_stock(product, quantity, db)

    cart = get_or_create_cart(db, user_id)
    item = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
        .first()
    )
    if item:
        item.quantity += quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.add(item)

    db.commit()
    db.refresh(cart)
    return cart


def clear_cart(db: Session, cart: Cart) -> None:
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()

