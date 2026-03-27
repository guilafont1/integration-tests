import pytest


@pytest.mark.integration
class TestListProducts:
    def test_liste_vide_au_demarrage(self, client):
        response = client.get("/products")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_produit_cree_apparait_dans_liste(self, client):
        created = client.post(
            "/products",
            json={"name": "Laptop", "price": 1000, "stock": 10, "category": "tech"},
        )
        assert created.status_code == 201
        response = client.get("/products")
        assert response.status_code == 200
        ids = [p["id"] for p in response.json()]
        assert created.json()["id"] in ids

    def test_filtre_par_categorie(self, client):
        client.post(
            "/products",
            json={"name": "GPU RTX", "price": 799.0, "stock": 3, "category": "gpu"},
        )
        response = client.get("/products?category=gpu")
        assert response.status_code == 200
        for p in response.json():
            assert p["category"] == "gpu"

    def test_pagination_limit(self, client):
        for i in range(5):
            client.post(
                "/products",
                json={"name": f"Prod{i}", "price": 10.0 + i, "stock": 1},
            )
        response = client.get("/products?limit=2")
        assert response.status_code == 200
        assert len(response.json()) <= 2

    def test_filtre_prix_min_max(self, client):
        in_range = client.post(
            "/products",
            json={"name": "Dans la fourchette", "price": 100.0, "stock": 4},
        ).json()
        out_low = client.post(
            "/products",
            json={"name": "Trop bas", "price": 20.0, "stock": 4},
        ).json()
        out_high = client.post(
            "/products",
            json={"name": "Trop haut", "price": 500.0, "stock": 4},
        ).json()

        response = client.get("/products?min_price=50&max_price=200")
        assert response.status_code == 200
        items = response.json()
        ids = {item["id"] for item in items}
        assert in_range["id"] in ids
        assert out_low["id"] not in ids
        assert out_high["id"] not in ids
        assert all(50 <= item["price"] <= 200 for item in items)


@pytest.mark.integration
class TestGetProduct:
    def test_get_produit_existant(self, client):
        created = client.post(
            "/products",
            json={"name": "Ecran", "price": 250.0, "stock": 3, "category": "display"},
        ).json()
        response = client.get(f"/products/{created['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created["id"]
        assert data["name"] == created["name"]

    def test_get_produit_inexistant_retourne_404(self, client):
        response = client.get("/products/99999")
        assert response.status_code == 404


@pytest.mark.integration
class TestCreateUpdateDeleteProduct:
    def test_creation_valide(self, client):
        payload = {"name": "Souris Ergonomique", "price": 49.99, "stock": 30}
        response = client.post("/products", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["price"] == payload["price"]
        assert data["id"] is not None

    def test_creation_prix_negatif_422(self, client):
        response = client.post(
            "/products",
            json={"name": "X", "price": -10.0, "stock": 5},
        )
        assert response.status_code == 422

    def test_creation_nom_vide_422(self, client):
        response = client.post(
            "/products",
            json={"name": "", "price": 10.0, "stock": 5},
        )
        assert response.status_code == 422

    def test_creation_stock_negatif_422(self, client):
        response = client.post(
            "/products",
            json={"name": "T", "price": 10.0, "stock": -1},
        )
        assert response.status_code == 422

    def test_mise_a_jour_prix(self, client):
        product = client.post(
            "/products",
            json={"name": "Produit MAJ", "price": 50.0, "stock": 2},
        ).json()
        response = client.put(
            f"/products/{product['id']}",
            json={"price": 79.99},
        )
        assert response.status_code == 200
        assert response.json()["price"] == 79.99

    def test_suppression_soft_delete(self, client):
        create = client.post(
            "/products",
            json={"name": "A supprimer", "price": 1.0, "stock": 1},
        )
        pid = create.json()["id"]
        response = client.delete(f"/products/{pid}")
        assert response.status_code == 204
        assert client.get(f"/products/{pid}").status_code == 404
