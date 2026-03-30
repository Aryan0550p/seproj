from flask import Flask, jsonify, request
from flask_cors import CORS

from services.store_service import StoreService

app = Flask(__name__)
CORS(app)
store = StoreService()


def _bad_request(message: str):
    return jsonify({"error": message}), 400


@app.get("/api/health")
def health_check():
    return jsonify({"status": "ok"})


@app.post("/api/reset")
def reset_store():
    state = store.reset_store()
    return jsonify({"message": "store reset", "products": len(state["products"]), "orders": len(state["orders"])})


@app.get("/api/products")
def get_products():
    return jsonify(store.get_products())


@app.post("/api/products")
def add_product():
    payload = request.get_json(silent=True) or {}
    if not payload.get("name"):
        return _bad_request("name is required")
    if payload.get("stock") is None:
        payload["stock"] = 0
    if payload.get("price") is None:
        payload["price"] = 0
    product = store.add_product(payload)
    return jsonify(product), 201


@app.patch("/api/products/<product_id>")
def update_product(product_id: str):
    payload = request.get_json(silent=True) or {}
    updated = store.update_product(product_id, payload)
    if not updated:
        return jsonify({"error": "product not found"}), 404
    return jsonify(updated)


@app.delete("/api/products/<product_id>")
def delete_product(product_id: str):
    deleted = store.delete_product(product_id)
    if not deleted:
        return jsonify({"error": "product not found"}), 404
    return jsonify({"message": "deleted"})


@app.get("/api/orders")
def get_orders():
    return jsonify(store.get_orders())


@app.post("/api/orders")
def add_order():
    payload = request.get_json(silent=True) or {}
    if not payload.get("customer"):
        return _bad_request("customer is required")
    if not isinstance(payload.get("items"), list) or not payload.get("items"):
        return _bad_request("items array is required")
    if payload.get("status") is None:
        payload["status"] = "Pending"
    if payload.get("payment") is None:
        payload["payment"] = "Unpaid"
    if payload.get("total") is None:
        payload["total"] = 0

    validation = store.validate_order_stock(payload.get("items", []))
    if not validation.get("isValid"):
        return jsonify(validation), 400

    created = store.add_order(payload)
    return jsonify(created), 201


@app.patch("/api/orders/<order_id>")
def update_order(order_id: str):
    payload = request.get_json(silent=True) or {}
    updated = store.update_order(order_id, payload)
    if not updated:
        return jsonify({"error": "order not found"}), 404
    return jsonify(updated)


@app.post("/api/orders/<order_id>/dispatch")
def dispatch_order(order_id: str):
    updated = store.dispatch_order(order_id)
    if not updated:
        return jsonify({"error": "order not found"}), 404
    return jsonify(updated)


@app.post("/api/orders/<order_id>/cancel")
def cancel_order(order_id: str):
    updated = store.cancel_order(order_id)
    if not updated:
        return jsonify({"error": "order not found"}), 404
    return jsonify(updated)


@app.get("/api/orders/<order_id>/completion")
def verify_order_completion(order_id: str):
    completion = store.verify_order_completion(order_id)
    if not completion:
        return jsonify({"error": "order not found"}), 404
    return jsonify(completion)


@app.post("/api/orders/validate-stock")
def validate_order_stock():
    payload = request.get_json(silent=True) or {}
    items = payload.get("items")
    if not isinstance(items, list):
        return _bad_request("items array is required")
    return jsonify(store.validate_order_stock(items))


@app.get("/api/activity-logs")
def get_activity_logs():
    return jsonify(store.get_activity_logs())


@app.get("/api/alerts")
def get_alerts():
    return jsonify(store.get_alerts())


@app.get("/api/alerts/active")
def get_active_alerts():
    return jsonify(store.get_active_alerts())


@app.patch("/api/alerts/<alert_id>/resolve")
def resolve_alert(alert_id: str):
    alert = store.resolve_alert(alert_id)
    if not alert:
        return jsonify({"error": "alert not found"}), 404
    return jsonify(alert)


@app.get("/api/notifications")
def get_notifications():
    recipient = request.args.get("recipient")
    if recipient:
        return jsonify(store.get_notifications_for_recipient(recipient))
    return jsonify(store.get_notifications())


@app.post("/api/inventory/adjust")
def adjust_stock():
    payload = request.get_json(silent=True) or {}
    product_id = payload.get("productId")
    adjustment_qty = payload.get("adjustmentQty")
    reason = payload.get("reason", "manual")

    if product_id is None or adjustment_qty is None:
        return _bad_request("productId and adjustmentQty are required")

    adjustment = store.adjust_stock(str(product_id), float(adjustment_qty), str(reason))
    if not adjustment:
        return jsonify({"error": "product not found"}), 404
    return jsonify(adjustment)


@app.post("/api/inventory/samples")
def record_sample_distribution():
    payload = request.get_json(silent=True) or {}
    product_id = payload.get("productId")
    quantity = payload.get("quantity")
    recipient_type = payload.get("recipientType", "unknown")

    if product_id is None or quantity is None:
        return _bad_request("productId and quantity are required")

    record = store.record_sample_distribution(str(product_id), float(quantity), str(recipient_type))
    if not record:
        return jsonify({"error": "product not found"}), 404
    return jsonify(record), 201


@app.get("/api/inventory/samples")
def get_sample_distributions():
    return jsonify(store.get_sample_distributions())


@app.post("/api/inventory/physical-stock")
def record_physical_stock():
    payload = request.get_json(silent=True) or {}
    product_id = payload.get("productId")
    physical_count = payload.get("physicalCount")

    if product_id is None or physical_count is None:
        return _bad_request("productId and physicalCount are required")

    record = store.record_physical_stock(str(product_id), float(physical_count))
    if not record:
        return jsonify({"error": "product not found"}), 404
    return jsonify(record), 201


@app.get("/api/inventory/physical-stock")
def get_physical_stock_records():
    return jsonify(store.get_physical_stock_records())


@app.get("/api/inventory/mismatches")
def get_stock_mismatches():
    return jsonify(store.get_stock_mismatches())


@app.get("/api/inventory/adjustments")
def get_stock_adjustments():
    return jsonify(store.get_stock_adjustments())


@app.get("/api/payments/pending")
def get_pending_payments():
    return jsonify(store.get_pending_payment_stats())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
