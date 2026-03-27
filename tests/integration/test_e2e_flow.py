def test_full_flow_e2e(client):
    product = {
        "name": "Phone",
        "price": 500,
        "stock": 10,
        "category": "tech",
    }
    res = client.post("/products", json=product)
    assert res.status_code == 201
    product_id = res.json()["id"]

    user_id = 1
    res = client.post(
        f"/cart/{user_id}/items",
        json={"product_id": product_id, "quantity": 2},
    )
    assert res.status_code == 201

    res = client.post("/orders", json={"user_id": user_id})
    assert res.status_code == 201
    assert res.json()["total_ttc"] > 0
