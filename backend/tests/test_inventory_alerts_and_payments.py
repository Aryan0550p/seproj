def test_adjust_stock_creates_adjustment_and_updates_product(client):
    response = client.post(
        "/api/inventory/adjust",
        json={"productId": "P001", "adjustmentQty": -5, "reason": "cycle_count"},
    )
    body = response.get_json()
    adjustments = client.get("/api/inventory/adjustments").get_json()
    updated_product = next(product for product in client.get("/api/products").get_json() if product["id"] == "P001")

    assert response.status_code == 200
    assert body["productId"] == "P001"
    assert body["reason"] == "cycle_count"
    assert body["newStock"] == 145.0
    assert adjustments[0]["id"] == body["id"]
    assert updated_product["stock"] == 145.0


def test_adjust_stock_requires_required_fields(client):
    response = client.post("/api/inventory/adjust", json={"productId": "P001"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "productId and adjustmentQty are required"}


def test_record_sample_distribution_creates_record_and_stock_adjustment(client):
    response = client.post(
        "/api/inventory/samples",
        json={"productId": "P001", "quantity": 3, "recipientType": "retailer"},
    )
    body = response.get_json()
    sample_records = client.get("/api/inventory/samples").get_json()
    adjustments = client.get("/api/inventory/adjustments").get_json()

    assert response.status_code == 201
    assert body["productId"] == "P001"
    assert body["quantity"] == 3
    assert sample_records[0]["id"] == body["id"]
    assert adjustments[0]["reason"] == "sample_distribution_retailer"


def test_record_sample_distribution_returns_404_for_unknown_product(client):
    response = client.post(
        "/api/inventory/samples",
        json={"productId": "P404", "quantity": 2, "recipientType": "retailer"},
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "product not found"}


def test_record_physical_stock_creates_alert_and_notification_on_mismatch(client):
    response = client.post(
        "/api/inventory/physical-stock",
        json={"productId": "P001", "physicalCount": 138},
    )
    body = response.get_json()
    mismatches = client.get("/api/inventory/mismatches").get_json()
    active_alerts = client.get("/api/alerts/active").get_json()
    warehouse_notifications = client.get("/api/notifications?recipient=warehouse_manager").get_json()

    assert response.status_code == 201
    assert body["productId"] == "P001"
    assert body["variance"] == -12.0
    assert len(mismatches) == 1
    assert len(active_alerts) == 1
    assert active_alerts[0]["entityId"] == "P001"
    assert len(warehouse_notifications) == 1


def test_resolve_alert_marks_alert_as_resolved(client):
    client.post("/api/inventory/physical-stock", json={"productId": "P001", "physicalCount": 138})
    alert = client.get("/api/alerts/active").get_json()[0]

    response = client.patch(f"/api/alerts/{alert['id']}/resolve")
    body = response.get_json()
    active_alerts = client.get("/api/alerts/active").get_json()

    assert response.status_code == 200
    assert body["status"] == "resolved"
    assert body["resolvedAt"] is not None
    assert active_alerts == []


def test_resolve_alert_returns_404_for_unknown_id(client):
    response = client.patch("/api/alerts/ALT-404/resolve")

    assert response.status_code == 404
    assert response.get_json() == {"error": "alert not found"}


def test_activity_logs_capture_inventory_events(client):
    client.post("/api/inventory/adjust", json={"productId": "P001", "adjustmentQty": -2, "reason": "audit"})

    response = client.get("/api/activity-logs")
    logs = response.get_json()

    assert response.status_code == 200
    assert len(logs) >= 1
    assert logs[0]["action"] == "STOCK_ADJUSTED"
    assert logs[0]["entityId"] == "P001"


def test_pending_payments_returns_current_unpaid_summary(client):
    response = client.get("/api/payments/pending")
    body = response.get_json()

    assert response.status_code == 200
    assert body["count"] == 3
    assert body["totalAmount"] == 52500.0
    assert len(body["orders"]) == 3


def test_notifications_endpoint_returns_all_and_filtered_results(client):
    client.post("/api/inventory/physical-stock", json={"productId": "P001", "physicalCount": 138})

    all_notifications = client.get("/api/notifications")
    warehouse_notifications = client.get("/api/notifications?recipient=warehouse_manager")

    assert all_notifications.status_code == 200
    assert warehouse_notifications.status_code == 200
    assert len(all_notifications.get_json()) == 1
    assert len(warehouse_notifications.get_json()) == 1
    assert warehouse_notifications.get_json()[0]["recipient"] == "warehouse_manager"
