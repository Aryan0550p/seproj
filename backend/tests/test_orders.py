def test_get_orders_returns_normalized_completion_fields(client):
    response = client.get("/api/orders")
    orders = response.get_json()

    assert response.status_code == 200
    assert len(orders) == 5
    assert all("deliveryConfirmed" in order for order in orders)
    assert all("paymentCompleted" in order for order in orders)
    assert all("isFinalized" in order for order in orders)


def test_add_order_creates_order_and_keeps_completion_state(valid_order_payload, client):
    response = client.post("/api/orders", json=valid_order_payload)
    body = response.get_json()

    assert response.status_code == 201
    assert body["id"] == "ORD-1006"
    assert body["customer"] == "QA Retail Partner"
    assert body["status"] == "Pending"
    assert body["payment"] == "Unpaid"
    assert body["deliveryConfirmed"] is False
    assert body["paymentCompleted"] is False
    assert body["isFinalized"] is False


def test_add_order_requires_customer(client, valid_order_payload):
    payload = dict(valid_order_payload)
    payload.pop("customer")

    response = client.post("/api/orders", json=payload)

    assert response.status_code == 400
    assert response.get_json() == {"error": "customer is required"}


def test_add_order_requires_items_array(client):
    response = client.post("/api/orders", json={"customer": "QA Retail Partner"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "items array is required"}


def test_add_order_rejects_insufficient_stock(client, valid_order_payload):
    payload = dict(valid_order_payload)
    payload["items"] = [
        {
            "productId": "P001",
            "name": "Premium Coffee Beans",
            "qty": 999,
            "price": 1200,
        }
    ]
    payload["total"] = 999 * 1200

    response = client.post("/api/orders", json=payload)
    body = response.get_json()

    assert response.status_code == 400
    assert body["isValid"] is False
    assert body["issues"][0]["productId"] == "P001"


def test_update_order_can_finalize_after_delivery_and_payment(client, valid_order_payload):
    created = client.post("/api/orders", json=valid_order_payload).get_json()

    response = client.patch(
        f"/api/orders/{created['id']}",
        json={"status": "Delivered", "payment": "Paid"},
    )
    body = response.get_json()

    assert response.status_code == 200
    assert body["status"] == "Delivered"
    assert body["payment"] == "Paid"
    assert body["deliveryConfirmed"] is True
    assert body["paymentCompleted"] is True
    assert body["isFinalized"] is True
    assert body["finalizedAt"] is not None


def test_update_order_returns_404_for_unknown_id(client):
    response = client.patch("/api/orders/ORD-9999", json={"status": "Delivered"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "order not found"}


def test_dispatch_order_reduces_stock_and_marks_order_shipped(client, valid_order_payload):
    starting_stock = next(product for product in client.get("/api/products").get_json() if product["id"] == "P001")["stock"]
    created = client.post("/api/orders", json=valid_order_payload).get_json()

    response = client.post(f"/api/orders/{created['id']}/dispatch")
    body = response.get_json()
    updated_stock = next(product for product in client.get("/api/products").get_json() if product["id"] == "P001")["stock"]

    assert response.status_code == 200
    assert body["status"] == "Shipped"
    assert updated_stock == starting_stock - 2


def test_cancel_order_restores_stock_after_dispatch(client, valid_order_payload):
    starting_stock = next(product for product in client.get("/api/products").get_json() if product["id"] == "P001")["stock"]
    created = client.post("/api/orders", json=valid_order_payload).get_json()

    client.post(f"/api/orders/{created['id']}/dispatch")
    response = client.post(f"/api/orders/{created['id']}/cancel")
    body = response.get_json()
    final_stock = next(product for product in client.get("/api/products").get_json() if product["id"] == "P001")["stock"]

    assert response.status_code == 200
    assert body["status"] == "Cancelled"
    assert final_stock == starting_stock


def test_verify_order_completion_reports_finalized_state(client, valid_order_payload):
    created = client.post("/api/orders", json=valid_order_payload).get_json()
    client.patch(f"/api/orders/{created['id']}", json={"status": "Delivered", "payment": "Paid"})

    response = client.get(f"/api/orders/{created['id']}/completion")
    body = response.get_json()

    assert response.status_code == 200
    assert body["orderId"] == created["id"]
    assert body["deliveryConfirmed"] is True
    assert body["paymentCompleted"] is True
    assert body["canFinalize"] is True
    assert body["finalizedAt"] is not None


def test_validate_order_stock_returns_issue_details_for_invalid_items(client):
    response = client.post(
        "/api/orders/validate-stock",
        json={
            "items": [
                {"productId": "P001", "qty": 999},
                {"productId": "P404", "qty": 1},
            ]
        },
    )
    body = response.get_json()

    assert response.status_code == 200
    assert body["isValid"] is False
    assert len(body["issues"]) == 2
    assert {issue["productId"] for issue in body["issues"]} == {"P001", "P404"}


def test_validate_order_stock_requires_items_array(client):
    response = client.post("/api/orders/validate-stock", json={"items": "not-a-list"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "items array is required"}
