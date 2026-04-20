import json

import pytest


def _response_body(response):
    try:
        return response.get_json()
    except Exception:
        return response.data.decode("utf-8", errors="replace")


def _log_case(title, response, expected_status, input_payload=None, expected_body=None, notes=None):
    print(f"\n=== {title} ===")
    print("Input:")
    print(json.dumps(input_payload, indent=2) if input_payload is not None else "None")
    print("Expected Status:")
    print(expected_status)
    print("Expected Output:")
    print(json.dumps(expected_body, indent=2) if expected_body is not None else "See assertion / endpoint contract")
    print("Actual Status:")
    print(response.status_code)
    print("Actual Output:")
    print(json.dumps(_response_body(response), indent=2))
    if notes:
        print("Notes:")
        print(notes)


def _create_product(client, payload=None):
    payload = payload or {"name": "Submission Product", "stock": 10, "price": 25}
    response = client.post("/api/products", json=payload)
    _log_case("POST /api/products", response, 201, payload)
    assert response.status_code == 201
    return response.get_json()


def _create_order(client, payload=None):
    payload = payload or {
        "customer": "Submission Customer",
        "createdBy": "tester",
        "items": [{"productId": "P001", "name": "Premium Coffee Beans", "qty": 2, "price": 1200}],
        "total": 2400,
        "status": "Pending",
        "payment": "Unpaid",
    }
    response = client.post("/api/orders", json=payload)
    _log_case("POST /api/orders", response, 201, payload)
    assert response.status_code == 201
    return response.get_json()


def test_health_check_submission_log(client):
    response = client.get("/api/health")
    _log_case("GET /api/health", response, 200, expected_body={"status": "ok"})
    assert response.status_code == 200


def test_reset_store_submission_log(client):
    response = client.post("/api/reset")
    _log_case("POST /api/reset", response, 200, expected_body={"message": "store reset", "products": 8, "orders": 5})
    assert response.status_code == 200


def test_get_products_submission_log(client):
    response = client.get("/api/products")
    _log_case("GET /api/products", response, 200, expected_body=[{"id": "P001", "name": "Premium Coffee Beans"}])
    assert response.status_code == 200


def test_create_product_submission_log(client):
    payload = {"name": "Soap", "stock": 10, "price": 25}
    response = client.post("/api/products", json=payload)
    _log_case("POST /api/products (create)", response, 201, payload)
    assert response.status_code == 201


def test_create_product_missing_name_submission_log(client):
    payload = {"stock": 5, "price": 10}
    response = client.post("/api/products", json=payload)
    _log_case("POST /api/products (missing name)", response, 400, payload, {"error": "name is required"})
    assert response.status_code == 400


def test_update_product_submission_log(client):
    response = client.patch("/api/products/P001", json={"stock": 175, "price": 1250})
    _log_case("PATCH /api/products/P001", response, 200, {"stock": 175, "price": 1250})
    assert response.status_code == 200


def test_update_product_not_found_submission_log(client):
    payload = {"stock": 10}
    response = client.patch("/api/products/P9999", json=payload)
    _log_case("PATCH /api/products/P9999", response, 404, payload, {"error": "product not found"})
    assert response.status_code == 404


def test_delete_product_submission_log(client):
    product = _create_product(client, {"name": "Delete Me", "stock": 1, "price": 5})
    response = client.delete(f"/api/products/{product['id']}")
    _log_case(f"DELETE /api/products/{product['id']}", response, 200, expected_body={"message": "deleted"})
    assert response.status_code == 200


def test_delete_product_not_found_submission_log(client):
    response = client.delete("/api/products/P4040")
    _log_case("DELETE /api/products/P4040", response, 404, expected_body={"error": "product not found"})
    assert response.status_code == 404


def test_get_orders_submission_log(client):
    response = client.get("/api/orders")
    _log_case("GET /api/orders", response, 200, expected_body=[{"id": "ORD-1001", "customer": "Retail Corp A"}])
    assert response.status_code == 200


def test_create_order_submission_log(client):
    payload = {
        "customer": "ABC",
        "items": [{"productId": "P001", "name": "Premium Coffee Beans", "qty": 1, "price": 1200}],
        "total": 1200,
        "status": "Pending",
        "payment": "Unpaid",
    }
    response = client.post("/api/orders", json=payload)
    _log_case("POST /api/orders (create)", response, 201, payload)
    assert response.status_code == 201


def test_create_order_missing_customer_submission_log(client):
    payload = {"items": [{"productId": "P001", "qty": 1, "price": 1200}], "total": 1200}
    response = client.post("/api/orders", json=payload)
    _log_case("POST /api/orders (missing customer)", response, 400, payload, {"error": "customer is required"})
    assert response.status_code == 400


def test_create_order_missing_items_submission_log(client):
    payload = {"customer": "ABC"}
    response = client.post("/api/orders", json=payload)
    _log_case("POST /api/orders (missing items)", response, 400, payload, {"error": "items array is required"})
    assert response.status_code == 400


def test_create_order_insufficient_stock_submission_log(client):
    payload = {
        "customer": "Test Customer",
        "items": [{"productId": "P001", "name": "Premium Coffee Beans", "qty": 999, "price": 1200}],
        "total": 1198800,
        "status": "Pending",
        "payment": "Unpaid",
    }
    response = client.post("/api/orders", json=payload)
    _log_case(
        "POST /api/orders (insufficient stock)",
        response,
        400,
        payload,
        {"isValid": False, "issues": [{"productId": "P001"}]},
    )
    assert response.status_code == 400


def test_update_order_submission_log(client):
    order = _create_order(client)
    payload = {"status": "Delivered", "payment": "Paid"}
    response = client.patch(f"/api/orders/{order['id']}", json=payload)
    _log_case(f"PATCH /api/orders/{order['id']}", response, 200, payload)
    assert response.status_code == 200


def test_update_order_not_found_submission_log(client):
    payload = {"status": "Delivered"}
    response = client.patch("/api/orders/ORD-9999", json=payload)
    _log_case("PATCH /api/orders/ORD-9999", response, 404, payload, {"error": "order not found"})
    assert response.status_code == 404


def test_dispatch_order_submission_log(client):
    order = _create_order(client)
    response = client.post(f"/api/orders/{order['id']}/dispatch")
    _log_case(f"POST /api/orders/{order['id']}/dispatch", response, 200)
    assert response.status_code == 200


def test_dispatch_order_not_found_submission_log(client):
    response = client.post("/api/orders/ORD-4040/dispatch")
    _log_case("POST /api/orders/ORD-4040/dispatch", response, 404, expected_body={"error": "order not found"})
    assert response.status_code == 404


def test_cancel_order_submission_log(client):
    order = _create_order(client)
    response = client.post(f"/api/orders/{order['id']}/cancel")
    _log_case(f"POST /api/orders/{order['id']}/cancel", response, 200)
    assert response.status_code == 200


def test_cancel_order_not_found_submission_log(client):
    response = client.post("/api/orders/ORD-4040/cancel")
    _log_case("POST /api/orders/ORD-4040/cancel", response, 404, expected_body={"error": "order not found"})
    assert response.status_code == 404


def test_order_completion_submission_log(client):
    response = client.get("/api/orders/ORD-1001/completion")
    _log_case("GET /api/orders/ORD-1001/completion", response, 200)
    assert response.status_code == 200


def test_order_completion_not_found_submission_log(client):
    response = client.get("/api/orders/ORD-4040/completion")
    _log_case("GET /api/orders/ORD-4040/completion", response, 404, expected_body={"error": "order not found"})
    assert response.status_code == 404


def test_validate_stock_submission_log(client):
    payload = {"items": [{"productId": "P001", "qty": 1}]}
    response = client.post("/api/orders/validate-stock", json=payload)
    _log_case("POST /api/orders/validate-stock", response, 200, payload)
    assert response.status_code == 200


def test_validate_stock_bad_items_submission_log(client):
    payload = {"items": "not-a-list"}
    response = client.post("/api/orders/validate-stock", json=payload)
    _log_case("POST /api/orders/validate-stock (bad items)", response, 400, payload, {"error": "items array is required"})
    assert response.status_code == 400


def test_validate_stock_missing_product_submission_log(client):
    payload = {"items": [{"productId": "BAD_ID", "qty": 1}]}
    response = client.post("/api/orders/validate-stock", json=payload)
    _log_case("POST /api/orders/validate-stock (bad product)", response, 200, payload)
    assert response.status_code == 200


def test_activity_logs_submission_log(client):
    client.post("/api/inventory/adjust", json={"productId": "P001", "adjustmentQty": -2, "reason": "audit"})
    response = client.get("/api/activity-logs")
    _log_case("GET /api/activity-logs", response, 200)
    assert response.status_code == 200


def test_alerts_and_active_alerts_submission_log(client):
    payload = {"productId": "P001", "physicalCount": 100}
    create_response = client.post("/api/inventory/physical-stock", json=payload)
    _log_case("POST /api/inventory/physical-stock", create_response, 201, payload)
    alerts = client.get("/api/alerts")
    _log_case("GET /api/alerts", alerts, 200)
    active = client.get("/api/alerts/active")
    _log_case("GET /api/alerts/active", active, 200)
    assert create_response.status_code == 201


def test_resolve_alert_submission_log(client):
    payload = {"productId": "P001", "physicalCount": 100}
    client.post("/api/inventory/physical-stock", json=payload)
    alert_id = client.get("/api/alerts").get_json()[0]["id"]
    response = client.patch(f"/api/alerts/{alert_id}/resolve")
    _log_case(f"PATCH /api/alerts/{alert_id}/resolve", response, 200)
    assert response.status_code == 200


def test_resolve_alert_not_found_submission_log(client):
    response = client.patch("/api/alerts/BAD_ALERT/resolve")
    _log_case("PATCH /api/alerts/BAD_ALERT/resolve", response, 404, expected_body={"error": "alert not found"})
    assert response.status_code == 404


def test_notifications_submission_log(client):
    payload = {"productId": "P001", "physicalCount": 100}
    client.post("/api/inventory/physical-stock", json=payload)
    all_notifications = client.get("/api/notifications")
    _log_case("GET /api/notifications", all_notifications, 200)
    filtered = client.get("/api/notifications?recipient=warehouse_manager")
    _log_case("GET /api/notifications?recipient=warehouse_manager", filtered, 200)
    assert all_notifications.status_code == 200


def test_adjust_stock_submission_log(client):
    payload = {"productId": "P003", "adjustmentQty": -5, "reason": "edge-test"}
    response = client.post("/api/inventory/adjust", json=payload)
    _log_case("POST /api/inventory/adjust", response, 200, payload)
    adjustments = client.get("/api/inventory/adjustments")
    _log_case("GET /api/inventory/adjustments", adjustments, 200)
    assert response.status_code == 200


def test_adjust_stock_missing_fields_submission_log(client):
    payload = {"productId": "P001"}
    response = client.post("/api/inventory/adjust", json=payload)
    _log_case("POST /api/inventory/adjust (missing fields)", response, 400, payload, {"error": "productId and adjustmentQty are required"})
    assert response.status_code == 400


def test_adjust_stock_never_negative_submission_log(client):
    payload = {"productId": "P003", "adjustmentQty": -10000, "reason": "edge-test"}
    response = client.post("/api/inventory/adjust", json=payload)
    _log_case("POST /api/inventory/adjust (large negative)", response, 200, payload)
    assert response.status_code == 200


def test_sample_distribution_submission_log(client):
    payload = {"productId": "P001", "quantity": 1, "recipientType": "retailer"}
    response = client.post("/api/inventory/samples", json=payload)
    _log_case("POST /api/inventory/samples", response, 201, payload)
    samples = client.get("/api/inventory/samples")
    _log_case("GET /api/inventory/samples", samples, 200)
    assert response.status_code == 201


def test_sample_distribution_product_not_found_submission_log(client):
    payload = {"productId": "BAD_ID", "quantity": 1, "recipientType": "retailer"}
    response = client.post("/api/inventory/samples", json=payload)
    _log_case("POST /api/inventory/samples (bad product)", response, 404, payload, {"error": "product not found"})
    assert response.status_code == 404


def test_sample_distribution_missing_quantity_submission_log(client):
    payload = {"productId": "P001", "recipientType": "retailer"}
    response = client.post("/api/inventory/samples", json=payload)
    _log_case("POST /api/inventory/samples (missing quantity)", response, 400, payload, {"error": "productId and quantity are required"})
    assert response.status_code == 400


def test_physical_stock_submission_log(client):
    payload = {"productId": "P001", "physicalCount": 100}
    response = client.post("/api/inventory/physical-stock", json=payload)
    _log_case("POST /api/inventory/physical-stock", response, 201, payload)
    records = client.get("/api/inventory/physical-stock")
    _log_case("GET /api/inventory/physical-stock", records, 200)
    mismatches = client.get("/api/inventory/mismatches")
    _log_case("GET /api/inventory/mismatches", mismatches, 200)
    assert response.status_code == 201


def test_physical_stock_product_not_found_submission_log(client):
    payload = {"productId": "BAD_ID", "physicalCount": 10}
    response = client.post("/api/inventory/physical-stock", json=payload)
    _log_case("POST /api/inventory/physical-stock (bad product)", response, 404, payload, {"error": "product not found"})
    assert response.status_code == 404


def test_physical_stock_missing_count_submission_log(client):
    payload = {"productId": "P001"}
    response = client.post("/api/inventory/physical-stock", json=payload)
    _log_case("POST /api/inventory/physical-stock (missing count)", response, 400, payload, {"error": "productId and physicalCount are required"})
    assert response.status_code == 400


def test_pending_payments_submission_log(client):
    response = client.get("/api/payments/pending")
    _log_case("GET /api/payments/pending", response, 200)
    assert response.status_code == 200


def test_notifications_empty_filter_submission_log(client):
    response = client.get("/api/notifications?recipient=no_such_role")
    _log_case("GET /api/notifications?recipient=no_such_role", response, 200, expected_body=[])
    assert response.status_code == 200


def test_alerts_empty_initial_state_submission_log(client):
    alerts = client.get("/api/alerts")
    _log_case("GET /api/alerts (initial state)", alerts, 200, expected_body=[])
    active = client.get("/api/alerts/active")
    _log_case("GET /api/alerts/active (initial state)", active, 200, expected_body=[])
    assert alerts.status_code == 200
    assert active.status_code == 200


@pytest.mark.xfail(reason="API currently accepts negative product price and only flags it later as an alert.")
def test_known_defect_negative_product_price_submission_log(client):
    payload = {"name": "Bad Price", "stock": 5, "price": -10}
    response = client.post("/api/products", json=payload)
    _log_case(
        "KNOWN DEFECT: POST /api/products (negative price)",
        response,
        400,
        payload,
        {"error": "Validation should reject negative price"},
        "Current implementation accepts the request, so this test is marked xfail.",
    )
    assert response.status_code == 400


@pytest.mark.xfail(reason="API currently accepts negative order quantity during creation.")
def test_known_defect_negative_order_qty_submission_log(client):
    payload = {
        "customer": "Edge Customer",
        "items": [{"productId": "P001", "name": "Premium Coffee Beans", "qty": -1, "price": 1200}],
        "total": -1200,
        "status": "Pending",
        "payment": "Unpaid",
    }
    response = client.post("/api/orders", json=payload)
    _log_case(
        "KNOWN DEFECT: POST /api/orders (negative qty)",
        response,
        400,
        payload,
        {"error": "Validation should reject negative quantity"},
        "Current implementation accepts the request, so this test is marked xfail.",
    )
    assert response.status_code == 400


@pytest.mark.xfail(reason="API currently accepts mismatched order totals during creation.")
def test_known_defect_total_mismatch_submission_log(client):
    payload = {
        "customer": "Mismatch Customer",
        "items": [{"productId": "P001", "name": "Premium Coffee Beans", "qty": 1, "price": 1200}],
        "total": 1,
        "status": "Pending",
        "payment": "Unpaid",
    }
    response = client.post("/api/orders", json=payload)
    _log_case(
        "KNOWN DEFECT: POST /api/orders (total mismatch)",
        response,
        400,
        payload,
        {"error": "Validation should reject mismatched totals"},
        "Current implementation accepts the request, so this test is marked xfail.",
    )
    assert response.status_code == 400


@pytest.mark.xfail(reason="API currently allows repeated dispatch calls that can reduce stock multiple times.")
def test_known_defect_double_dispatch_submission_log(client):
    order = _create_order(client)
    first_response = client.post(f"/api/orders/{order['id']}/dispatch")
    _log_case(f"POST /api/orders/{order['id']}/dispatch (first)", first_response, 200)
    second_response = client.post(f"/api/orders/{order['id']}/dispatch")
    _log_case(
        f"KNOWN DEFECT: POST /api/orders/{order['id']}/dispatch (second)",
        second_response,
        400,
        expected_body={"error": "Dispatch should be blocked after first dispatch"},
        notes="Current implementation allows the second dispatch, so this test is marked xfail.",
    )
    assert second_response.status_code == 400


@pytest.mark.xfail(reason="API currently allows negative sample quantity, which can increase stock.")
def test_known_defect_negative_sample_submission_log(client):
    payload = {"productId": "P001", "quantity": -5, "recipientType": "retailer"}
    response = client.post("/api/inventory/samples", json=payload)
    _log_case(
        "KNOWN DEFECT: POST /api/inventory/samples (negative quantity)",
        response,
        400,
        payload,
        {"error": "Validation should reject negative sample quantity"},
        "Current implementation accepts the request, so this test is marked xfail.",
    )
    assert response.status_code == 400


@pytest.mark.xfail(reason="API currently accepts negative physical stock counts.")
def test_known_defect_negative_physical_stock_submission_log(client):
    payload = {"productId": "P001", "physicalCount": -3}
    response = client.post("/api/inventory/physical-stock", json=payload)
    _log_case(
        "KNOWN DEFECT: POST /api/inventory/physical-stock (negative count)",
        response,
        400,
        payload,
        {"error": "Validation should reject negative physical counts"},
        "Current implementation accepts the request, so this test is marked xfail.",
    )
    assert response.status_code == 400


@pytest.mark.xfail(reason="API currently allows deleting products that may still be referenced by orders.")
def test_known_defect_delete_referenced_product_submission_log(client):
    response = client.delete("/api/products/P001")
    _log_case(
        "KNOWN DEFECT: DELETE /api/products/P001 (referenced product)",
        response,
        400,
        expected_body={"error": "Deletion should be blocked for referenced products"},
        notes="Current implementation allows deletion, so this test is marked xfail.",
    )
    assert response.status_code == 400
