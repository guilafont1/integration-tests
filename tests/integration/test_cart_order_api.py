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
    assert created_product.status_code == 201
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
    assert added.status_code == 201
    cart_json = added.json()
    assert cart_json["user_id"] == user_id
    assert cart_json["items"][0]["product_id"] == product_id
    assert cart_json["items"][0]["quantity"] == quantity

    order = client.post(
        "/orders",
        json={"user_id": user_id, "coupon_code": "PROMO20"},
    )
    assert order.status_code == 201
    order_json = order.json()
    assert order_json["user_id"] == user_id
    assert order_json["coupon_code"] == "PROMO20"
    expected_total_ttc = 1920.0
    assert order_json["total_ttc"] == pytest.approx(expected_total_ttc)
    assert order_json["items"][0]["product_id"] == product_id
    assert order_json["items"][0]["quantity"] == quantity


def test_coupon_inexistant_retourne_404(client):
    created_product = client.post(
        "/products",
        json={
            "name": "Produit Coupon",
            "price": 100,
            "stock": 10,
            "category": "tech",
        },
    )
    product_id = created_product.json()["id"]
    user_id = 2
    client.post(
        f"/cart/{user_id}/items",
        json={"product_id": product_id, "quantity": 1},
    )

    response = client.post(
        "/orders",
        json={"user_id": user_id, "coupon_code": "FAKECODE"},
    )
    assert response.status_code == 404
    assert "Coupon introuvable" in response.json()["detail"]


def test_get_commande_par_id(client):
    created_product = client.post(
        "/products",
        json={"name": "Produit Commande", "price": 150, "stock": 10},
    )
    product_id = created_product.json()["id"]
    user_id = 3
    client.post(
        f"/cart/{user_id}/items",
        json={"product_id": product_id, "quantity": 2},
    )
    created_order = client.post("/orders", json={"user_id": user_id})
    assert created_order.status_code == 201
    oid = created_order.json()["id"]
    expected_total_ttc = created_order.json()["total_ttc"]

    response = client.get(f"/orders/{oid}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == oid
    assert data["total_ttc"] == pytest.approx(expected_total_ttc)


def test_transition_statut_commande(client):
    created_product = client.post(
        "/products",
        json={"name": "Produit Statut", "price": 99, "stock": 10},
    )
    product_id = created_product.json()["id"]
    user_id = 4
    client.post(
        f"/cart/{user_id}/items",
        json={"product_id": product_id, "quantity": 1},
    )
    order = client.post("/orders", json={"user_id": user_id}).json()

    ok = client.patch(
        f"/orders/{order['id']}/status",
        json={"status": "confirmed"},
    )
    assert ok.status_code == 200
    assert ok.json()["status"] == "confirmed"

    invalid = client.patch(
        f"/orders/{order['id']}/status",
        json={"status": "pending"},
    )
    assert invalid.status_code == 400
