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


def test_full_flow_e2e():
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
        # 1) créer produit
        product = {
            "name": "Phone",
            "price": 500,
            "stock": 10,
            "category": "tech",
        }
        res = client.post("/products", json=product)
        assert res.status_code == 200
        product_id = res.json()["id"]

        # 2) ajouter au panier
        user_id = 1
        res = client.post(
            f"/cart/{user_id}/items",
            json={"product_id": product_id, "quantity": 2},
        )
        assert res.status_code == 200

        # 3) créer commande
        res = client.post("/orders", json={"user_id": user_id})
        assert res.status_code == 200

        data = res.json()
        assert data["total_ttc"] > 0

    app.dependency_overrides.clear()
    engine.dispose()

