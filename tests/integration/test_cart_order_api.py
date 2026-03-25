import pytest


def test_cart_then_order_with_coupon(client):
    unit_price = 1000
    quantity = 2

    created_product = client.post(
        "/products",
        json={
            "name": "Phone",
            "price": unit_price,
            "stock": 10,
            "category": "tech",
        },
    )
    assert created_product.status_code == 200
    product_id = created_product.json()["id"]

    created_coupon = client.post(
        "/coupons", json={"code": "PROMO20", "reduction": 20, "actif": True}
    )
    assert created_coupon.status_code == 200

    user_id = 1
    added = client.post(
        f"/cart/{user_id}/items",
        json={"product_id": product_id, "quantity": quantity},
    )
    assert added.status_code == 200
    cart_json = added.json()
    assert cart_json["user_id"] == user_id
    assert cart_json["items"][0]["product_id"] == product_id
    assert cart_json["items"][0]["quantity"] == quantity

    order = client.post(
        "/orders",
        json={"user_id": user_id, "coupon_code": "PROMO20"},
    )
    assert order.status_code == 200
    order_json = order.json()
    assert order_json["user_id"] == user_id
    assert order_json["coupon_code"] == "PROMO20"
    expected_total_ttc = 1920.0
    assert order_json["total_ttc"] == pytest.approx(expected_total_ttc)
    assert order_json["items"][0]["product_id"] == product_id
    assert order_json["items"][0]["quantity"] == quantity
