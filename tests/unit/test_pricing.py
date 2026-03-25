import pytest

from app.models import Coupon, Product
from app.services.pricing import (
    appliquer_coupon,
    calcul_prix_ttc,
    calculer_total,
)


@pytest.mark.parametrize(
    ("prix_ht", "expected"),
    [
        (100, 120.0),
        (0, 0.0),
    ],
)
def test_calcul_prix_ttc_ok(prix_ht, expected):
    assert calcul_prix_ttc(prix_ht) == pytest.approx(expected)


def test_calcul_prix_ttc_negative():
    with pytest.raises(ValueError):
        calcul_prix_ttc(-10)


def test_appliquer_coupon_normal():
    coupon = Coupon(code="PROMO20", reduction=20, actif=True)
    assert appliquer_coupon(100, coupon) == pytest.approx(80.0)


def test_appliquer_coupon_inactif():
    coupon = Coupon(code="PROMO20", reduction=20, actif=False)
    with pytest.raises(ValueError):
        appliquer_coupon(100, coupon)


def test_appliquer_coupon_invalid_reduction():
    coupon = Coupon(code="PROMO", reduction=200, actif=True)
    with pytest.raises(ValueError):
        appliquer_coupon(100, coupon)


def test_calculer_total_empty():
    assert calculer_total([]) == pytest.approx(0.0)


def test_calculer_total_with_products():
    p1 = Product(price=100)
    p2 = Product(price=50)

    total = calculer_total([(p1, 1), (p2, 2)])
    assert total == pytest.approx(240.0)


def test_calculer_total_with_coupon():
    p1 = Product(price=100)
    coupon = Coupon(code="PROMO20", reduction=20, actif=True)

    total = calculer_total([(p1, 1)], coupon)
    assert total == pytest.approx(96.0)
