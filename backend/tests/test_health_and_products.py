def test_health_check_returns_ok(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_reset_store_restores_seed_counts(client):
    client.post("/api/products", json={"name": "Temp Product", "stock": 4, "price": 25})

    response = client.post("/api/reset")
    body = response.get_json()

    assert response.status_code == 200
    assert body["message"] == "store reset"
    assert body["products"] == 8
    assert body["orders"] == 5


def test_get_products_returns_seeded_products(client):
    response = client.get("/api/products")
    products = response.get_json()

    assert response.status_code == 200
    assert len(products) == 8
    assert products[0]["id"] == "P001"
    assert products[0]["name"] == "Premium Coffee Beans"


def test_add_product_creates_product_with_defaults(client):
    response = client.post("/api/products", json={"name": "Test Syrup"})
    body = response.get_json()

    assert response.status_code == 201
    assert body["id"] == "P0009"
    assert body["name"] == "Test Syrup"
    assert body["stock"] == 0
    assert body["price"] == 0


def test_add_product_requires_name(client):
    response = client.post("/api/products", json={"stock": 3, "price": 99})

    assert response.status_code == 400
    assert response.get_json() == {"error": "name is required"}


def test_update_product_changes_existing_product(client):
    response = client.patch("/api/products/P001", json={"stock": 175, "price": 1250})
    body = response.get_json()

    assert response.status_code == 200
    assert body["id"] == "P001"
    assert body["stock"] == 175
    assert body["price"] == 1250


def test_update_product_returns_404_for_unknown_id(client):
    response = client.patch("/api/products/P9999", json={"stock": 10})

    assert response.status_code == 404
    assert response.get_json() == {"error": "product not found"}


def test_delete_product_removes_existing_product(client):
    create_response = client.post("/api/products", json={"name": "Delete Me", "stock": 1, "price": 5})
    product_id = create_response.get_json()["id"]

    delete_response = client.delete(f"/api/products/{product_id}")
    products_response = client.get("/api/products")
    product_ids = {product["id"] for product in products_response.get_json()}

    assert delete_response.status_code == 200
    assert delete_response.get_json() == {"message": "deleted"}
    assert product_id not in product_ids


def test_delete_product_returns_404_for_unknown_id(client):
    response = client.delete("/api/products/P4040")

    assert response.status_code == 404
    assert response.get_json() == {"error": "product not found"}
