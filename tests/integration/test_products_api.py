def test_products_post_then_get(client):
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
    assert listed_json[0]["name"] == "Laptop"
