import pytest

from app.models import CartItem, Product
from app.services.cart import add_item, clear_cart, get_or_create_cart


def test_get_or_create_cart_cree_un_panier(db_session):
    cart = get_or_create_cart(db_session, user_id=42)
    assert cart.user_id == 42
    assert cart.id is not None


def test_get_or_create_cart_reutilise_le_panier(db_session):
    first = get_or_create_cart(db_session, user_id=77)
    second = get_or_create_cart(db_session, user_id=77)
    assert first.id == second.id


def test_add_item_ajoute_un_item(db_session, mocker):
    mocker.patch("app.services.stock.redis_client")
    product = Product(name="Mouse", price=39.9, stock=10)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    cart = add_item(db_session, user_id=100, product_id=product.id, quantity=2)
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 2
    assert product.stock == 8


def test_add_item_incremente_quantite_existante(db_session, mocker):
    mocker.patch("app.services.stock.redis_client")
    product = Product(name="Headset", price=89.0, stock=15)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    add_item(db_session, user_id=101, product_id=product.id, quantity=2)
    cart = add_item(db_session, user_id=101, product_id=product.id, quantity=3)
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 5


def test_add_item_quantite_invalide(db_session):
    with pytest.raises(ValueError, match="Quantité invalide"):
        add_item(db_session, user_id=1, product_id=1, quantity=0)


def test_add_item_produit_introuvable(db_session):
    with pytest.raises(ValueError, match="Produit introuvable"):
        add_item(db_session, user_id=1, product_id=999, quantity=1)


def test_clear_cart_supprime_les_items(db_session, mocker):
    mocker.patch("app.services.stock.redis_client")
    product = Product(name="Keyboard", price=120.0, stock=6)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    cart = add_item(db_session, user_id=555, product_id=product.id, quantity=1)
    assert len(cart.items) == 1

    clear_cart(db_session, cart)
    count = (
        db_session.query(CartItem).filter(CartItem.cart_id == cart.id).count()
    )
    assert count == 0
