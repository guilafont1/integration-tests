from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import create_app


def _make_test_engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_cart_then_order_with_coupon():
    engine = _make_test_engine()
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = create_app(engine=engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        # 1) Create a product with stock
        created_product = client.post(
            "/products",
            json={"name": "Phone", "price": 1000, "stock": 10, "category": "tech"},
        )
        assert created_product.status_code == 200
        product_id = created_product.json()["id"]

        # 2) Create a coupon
        created_coupon = client.post(
            "/coupons", json={"code": "PROMO20", "reduction": 20, "actif": True}
        )
        assert created_coupon.status_code == 200

        # 3) Add to cart (reserves stock)
        user_id = 1
        added = client.post(
            f"/cart/{user_id}/items", json={"product_id": product_id, "quantity": 2}
        )
        assert added.status_code == 200
        cart_json = added.json()
        assert cart_json["user_id"] == user_id
        assert len(cart_json["items"]) == 1
        assert cart_json["items"][0]["product_id"] == product_id
        assert cart_json["items"][0]["quantity"] == 2

        # 4) Create order with coupon
        order = client.post(
            "/orders", json={"user_id": user_id, "coupon_code": "PROMO20"}
        )
        assert order.status_code == 200
        order_json = order.json()
        assert order_json["user_id"] == user_id
        assert order_json["coupon_code"] == "PROMO20"
        # 2 * 1000 = 2000 HT -> 2400 TTC -> -20% = 1920
        assert order_json["total_ttc"] == 1920.0
        assert len(order_json["items"]) == 1
        assert order_json["items"][0]["product_id"] == product_id
        assert order_json["items"][0]["quantity"] == 2

    app.dependency_overrides.clear()
    engine.dispose()

