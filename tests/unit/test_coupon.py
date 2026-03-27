import pytest

from app.models import Coupon
from app.services.pricing import appliquer_coupon


def test_coupon_50_percent_refused():
    coupon = Coupon(code="PROMO50", reduction=50, actif=True)
    with pytest.raises(ValueError):
        appliquer_coupon(100, coupon)
