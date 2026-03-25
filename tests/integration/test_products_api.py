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


def test_products_post_then_get():
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
        create_payload = {
            "name": "Laptop",
            "price": 1000,
            "stock": 10,
            "category": "tech",
        }

        created = client.post("/products", json=create_payload)
        assert created.status_code == 200
        created_json = created.json()
        assert created_json["name"] == "Laptop"
        assert created_json["price"] == 1000
        assert created_json["stock"] == 10
        assert created_json["category"] == "tech"
        assert "id" in created_json
        assert "created_at" in created_json

        listed = client.get("/products")
        assert listed.status_code == 200
        listed_json = listed.json()
        assert isinstance(listed_json, list)
        assert len(listed_json) == 1
        assert listed_json[0]["name"] == "Laptop"

    app.dependency_overrides.clear()
    engine.dispose()

