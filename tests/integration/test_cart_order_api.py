def test_cart_then_order_with_coupon(client):
    created_product = client.post(
        "/products",
        json={"name": "Phone", "price": 1000, "stock": 10, "category": "tech"},
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
        json={"product_id": product_id, "quantity": 2},
    )
    assert added.status_code == 200
    cart_json = added.json()
    assert cart_json["user_id"] == user_id
    assert cart_json["items"][0]["product_id"] == product_id
    assert cart_json["items"][0]["quantity"] == 2

    order = client.post(
        "/orders",
        json={"user_id": user_id, "coupon_code": "PROMO20"},
    )
    assert order.status_code == 200
    order_json = order.json()
    assert order_json["user_id"] == user_id
    assert order_json["coupon_code"] == "PROMO20"
    assert order_json["total_ttc"] == 1920.0
    assert order_json["items"][0]["product_id"] == product_id
    assert order_json["items"][0]["quantity"] == 2
