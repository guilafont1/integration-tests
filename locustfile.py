from locust import HttpUser, between, task


class ShopFlowUser(HttpUser):
    host = "http://127.0.0.1:8000"
    wait_time = between(0.2, 1.0)

    @task(3)
    def get_products(self):
        self.client.get("/products")

    @task(1)
    def create_product(self):
        self.client.post(
            "/products",
            json={
                "name": "Test",
                "price": 100,
                "stock": 5,
                "category": "test",
            },
        )

