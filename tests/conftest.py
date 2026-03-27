import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402
from faker import Faker  # noqa: E402

from app.database import Base, get_db  # noqa: E402
from app.models import Coupon, Product  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture()
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture()
def db_session(test_engine):
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def product_sample(db_session):
    product = Product(name="Laptop Pro", price=999.99, stock=10)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture()
def coupon_sample(db_session):
    coupon = Coupon(code="PROMO20", reduction=20.0, actif=True)
    db_session.add(coupon)
    db_session.commit()
    db_session.refresh(coupon)
    return coupon


@pytest.fixture()
def client(test_engine, db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app = create_app(engine=test_engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


fake = Faker("fr_FR")


@pytest.fixture()
def fake_product_data():
    return {
        "name": fake.catch_phrase()[:50],
        "price": round(fake.pyfloat(min_value=1, max_value=2000, right_digits=2), 2),
        "stock": fake.random_int(min=0, max=500),
        "category": fake.random_element(
            ["informatique", "peripheriques", "audio", "gaming"]
        ),
    }


@pytest.fixture()
def multiple_products(client):
    products = []
    for i in range(5):
        response = client.post(
            "/products",
            json={
                "name": f"Produit {i}",
                "price": round(10.0 + i * 20, 2),
                "stock": 10,
            },
        )
        assert response.status_code == 201
        products.append(response.json())
    return products
