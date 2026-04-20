import pytest


def test_dispatch_order_unknown_id_returns_404(client):
    response = client.post("/api/orders/ORD-4040/dispatch")

    assert response.status_code == 404
    assert response.get_json() == {"error": "order not found"}


def test_cancel_order_unknown_id_returns_404(client):
    response = client.post("/api/orders/ORD-4040/cancel")

    assert response.status_code == 404
    assert response.get_json() == {"error": "order not found"}


def test_completion_unknown_id_returns_404(client):
    response = client.get("/api/orders/ORD-4040/completion")

    assert response.status_code == 404
    assert response.get_json() == {"error": "order not found"}


def test_adjust_stock_never_goes_below_zero(client):
    response = client.post(
        "/api/inventory/adjust",
        json={"productId": "P003", "adjustmentQty": -10000, "reason": "stress_test"},
    )
    body = response.get_json()

    assert response.status_code == 200
    assert body["newStock"] == 0.0


def test_notifications_filter_with_no_matching_recipient_returns_empty_list(client):
    response = client.get("/api/notifications?recipient=no_such_role")

    assert response.status_code == 200
    assert response.get_json() == []


def test_alert_endpoints_return_empty_lists_before_any_alert_is_created(client):
    all_alerts = client.get("/api/alerts")
    active_alerts = client.get("/api/alerts/active")

    assert all_alerts.status_code == 200
    assert active_alerts.status_code == 200
    assert all_alerts.get_json() == []
    assert active_alerts.get_json() == []


def test_sample_distribution_requires_quantity(client):
    response = client.post(
        "/api/inventory/samples",
        json={"productId": "P001", "recipientType": "retailer"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "productId and quantity are required"}


def test_physical_stock_requires_count(client):
    response = client.post("/api/inventory/physical-stock", json={"productId": "P001"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "productId and physicalCount are required"}


@pytest.mark.xfail(reason="API currently accepts negative product price and only flags it as an alert later.")
def test_create_product_negative_price_should_be_rejected(client):
    response = client.post(
        "/api/products",
        json={"name": "Bad Price Product", "stock": 5, "price": -10},
    )

    assert response.status_code == 400


@pytest.mark.xfail(reason="API currently accepts negative order quantity during creation.")
def test_create_order_negative_quantity_should_be_rejected(client):
    response = client.post(
        "/api/orders",
        json={
            "customer": "Edge Customer",
            "items": [{"productId": "P001", "name": "Premium Coffee Beans", "qty": -1, "price": 1200}],
            "total": -1200,
            "status": "Pending",
            "payment": "Unpaid",
        },
    )

    assert response.status_code == 400


@pytest.mark.xfail(reason="API currently accepts mismatched order totals during creation.")
def test_create_order_total_mismatch_should_be_rejected(client):
    response = client.post(
        "/api/orders",
        json={
            "customer": "Mismatch Customer",
            "items": [{"productId": "P001", "name": "Premium Coffee Beans", "qty": 1, "price": 1200}],
            "total": 1,
            "status": "Pending",
            "payment": "Unpaid",
        },
    )

    assert response.status_code == 400


@pytest.mark.xfail(reason="API currently allows repeated dispatch calls that can reduce stock multiple times.")
def test_dispatching_same_order_twice_should_be_blocked(client, valid_order_payload):
    created = client.post("/api/orders", json=valid_order_payload).get_json()

    first_response = client.post(f"/api/orders/{created['id']}/dispatch")
    second_response = client.post(f"/api/orders/{created['id']}/dispatch")

    assert first_response.status_code == 200
    assert second_response.status_code == 400


@pytest.mark.xfail(reason="API currently allows negative sample quantity, which can increase stock.")
def test_negative_sample_distribution_should_be_rejected(client):
    response = client.post(
        "/api/inventory/samples",
        json={"productId": "P001", "quantity": -5, "recipientType": "retailer"},
    )

    assert response.status_code == 400


@pytest.mark.xfail(reason="API currently accepts negative physical stock counts.")
def test_negative_physical_stock_should_be_rejected(client):
    response = client.post(
        "/api/inventory/physical-stock",
        json={"productId": "P001", "physicalCount": -3},
    )

    assert response.status_code == 400


@pytest.mark.xfail(reason="API currently allows deleting products that may still be referenced by orders.")
def test_delete_product_referenced_by_existing_order_should_be_blocked(client):
    response = client.delete("/api/products/P001")

    assert response.status_code == 400
