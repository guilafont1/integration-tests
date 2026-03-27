import pytest

from app.models import Product
from app.services.stock import liberer_stock, reserver_stock, verifier_stock

REDIS_MOCK_PATH = "app.services.stock.redis_client"


class TestVerifierStock:
    def test_stock_suffisant(self, product_sample):
        assert verifier_stock(product_sample, 5) is True

    def test_stock_insuffisant(self, product_sample):
        assert verifier_stock(product_sample, 999) is False

    def test_stock_exactement_disponible(self, product_sample):
        assert verifier_stock(product_sample, 10) is True

    def test_quantite_zero_leve_exception(self, product_sample):
        with pytest.raises(ValueError):
            verifier_stock(product_sample, 0)

    def test_quantite_negative_leve_exception(self, product_sample):
        with pytest.raises(ValueError):
            verifier_stock(product_sample, -1)


class TestReserverStock:
    def test_reservation_reussie(self, product_sample, db_session, mocker):
        mock_redis = mocker.patch(REDIS_MOCK_PATH)

        updated = reserver_stock(product_sample, 3, db_session)

        assert updated.stock == 7
        mock_redis.delete.assert_called_once_with(
            f"product:{product_sample.id}:stock"
        )

    def test_stock_insuffisant_leve_exception(
        self, product_sample, db_session, mocker
    ):
        mock_redis = mocker.patch(REDIS_MOCK_PATH)

        with pytest.raises(ValueError, match="insuffisant"):
            reserver_stock(product_sample, 999, db_session)

        mock_redis.delete.assert_not_called()


def test_liberation_stock(product_sample, db_session, mocker):
    mock_redis = mocker.patch(REDIS_MOCK_PATH)

    updated = liberer_stock(product_sample, 2, db_session)

    assert updated.stock == 12
    mock_redis.set.assert_called_once_with(
        f"product:{product_sample.id}:stock",
        updated.stock,
    )


def test_liberation_quantite_invalide(product_sample, db_session):
    with pytest.raises(ValueError):
        liberer_stock(product_sample, 0, db_session)


def test_reserver_stock_sur_produit_custom(db_session, mocker):
    mocker.patch(REDIS_MOCK_PATH)
    product = Product(name="USB", price=12.5, stock=3)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    reserver_stock(product, 2, db_session)
    assert product.stock == 1
