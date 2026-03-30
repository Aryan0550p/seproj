import json
import os
import random
import re
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.json")
MAX_ACTIVITY_LOGS = 1000

SEED_PRODUCTS = [
    {"id": "P001", "name": "Premium Coffee Beans", "category": "Beverages", "price": 1200, "unit": "kg", "stock": 150, "sku": "SKU001"},
    {"id": "P002", "name": "Organic Green Tea", "category": "Beverages", "price": 850, "unit": "kg", "stock": 80, "sku": "SKU002"},
    {"id": "P003", "name": "Whole Wheat Flour", "category": "Pantry", "price": 45, "unit": "kg", "stock": 500, "sku": "SKU003"},
    {"id": "P004", "name": "Almond Oil", "category": "Pantry", "price": 1500, "unit": "L", "stock": 0, "sku": "SKU004"},
    {"id": "P005", "name": "Raw Honey Crate", "category": "Pantry", "price": 4500, "unit": "10kg", "stock": 25, "sku": "SKU005"},
    {"id": "P006", "name": "Premium Rice 5kg", "category": "Grains", "price": 260, "unit": "5kg", "stock": 150, "sku": "SKU006"},
    {"id": "P007", "name": "Organic Sugar 2kg", "category": "Sweeteners", "price": 125, "unit": "2kg", "stock": 25, "sku": "SKU007"},
    {"id": "P008", "name": "Refined Oil 1L", "category": "Oils", "price": 88, "unit": "L", "stock": 0, "sku": "SKU008"},
]

SEED_ORDERS = [
    {"id": "ORD-1001", "customer": "Retail Corp A", "createdBy": "retailer1", "date": "2026-03-10", "items": [{"productId": "P001", "name": "Premium Coffee Beans", "qty": 10, "price": 1200}], "total": 12000, "status": "Delivered", "payment": "Paid"},
    {"id": "ORD-1002", "customer": "Shop B", "createdBy": "salesman1", "date": "2026-03-12", "items": [{"productId": "P003", "name": "Whole Wheat Flour", "qty": 100, "price": 45}], "total": 4500, "status": "Shipped", "payment": "Paid"},
    {"id": "ORD-1003", "customer": "Mart C", "createdBy": "retailer1", "date": "2026-03-15", "items": [{"productId": "P006", "name": "Premium Rice 5kg", "qty": 50, "price": 260}], "total": 13000, "status": "Pending", "payment": "Unpaid"},
    {"id": "ORD-1004", "customer": "Store D", "createdBy": "salesman1", "date": "2026-03-16", "items": [{"productId": "P002", "name": "Organic Green Tea", "qty": 20, "price": 850}], "total": 17000, "status": "Pending", "payment": "Unpaid"},
    {"id": "ORD-1005", "customer": "Retail Corp A", "createdBy": "retailer1", "date": "2026-03-17", "items": [{"productId": "P005", "name": "Raw Honey Crate", "qty": 5, "price": 4500}], "total": 22500, "status": "Shipped", "payment": "Unpaid"},
]


class StoreService:
    def __init__(self, data_file: str = DATA_FILE) -> None:
        self.data_file = data_file
        self._init_store()

    def _now_iso(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

    def _next_record_id(self, prefix: str) -> str:
        return f"{prefix}-{int(datetime.utcnow().timestamp() * 1000)}-{random.randint(100000, 999999)}"

    def _next_id(self, prefix: str, rows: List[Dict[str, Any]]) -> str:
        max_num = 0
        for item in rows:
            item_id = str(item.get("id", ""))
            m = re.search(r"(\d+)$", item_id)
            if m:
                max_num = max(max_num, int(m.group(1)))
        return f"{prefix}{str(max_num + 1).zfill(4)}"

    def _seed_state(self) -> Dict[str, Any]:
        seeded_orders = [self._apply_order_completion_state(order) for order in deepcopy(SEED_ORDERS)]
        return {
            "products": deepcopy(SEED_PRODUCTS),
            "orders": seeded_orders,
            "activity_logs": [],
            "alerts": [],
            "notifications": [],
            "sample_distributions": [],
            "physical_stocks": [],
            "stock_adjustments": [],
        }

    def _load_state(self) -> Dict[str, Any]:
        if not os.path.exists(self.data_file):
            return self._seed_state()

        with open(self.data_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        defaults = self._seed_state()
        for key, default_value in defaults.items():
            if key not in state or not isinstance(state[key], list):
                state[key] = default_value

        return state

    def _save_state(self, state: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def _init_store(self) -> None:
        state = self._load_state()
        self._save_state(state)
        self._run_global_discrepancy_checks(state)
        self._save_state(state)

    def reset_store(self) -> Dict[str, Any]:
        state = self._seed_state()
        self._run_global_discrepancy_checks(state)
        self._save_state(state)
        return state

    def _calculate_order_expected_total(self, order: Dict[str, Any]) -> float:
        total = 0.0
        for item in order.get("items", []) or []:
            qty = float(item.get("qty", 0) or 0)
            price = float(item.get("price", 0) or 0)
            total += qty * price
        return total

    def _evaluate_order_completion(self, order: Dict[str, Any]) -> Dict[str, Any]:
        delivery_confirmed = order.get("status") == "Delivered"
        payment_completed = order.get("payment") == "Paid"
        return {
            "deliveryConfirmed": delivery_confirmed,
            "paymentCompleted": payment_completed,
            "canFinalize": delivery_confirmed and payment_completed,
        }

    def _apply_order_completion_state(self, order: Dict[str, Any], previous_order: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        completion = self._evaluate_order_completion(order)
        finalized_at = None
        if completion["canFinalize"]:
            finalized_at = order.get("finalizedAt") or (previous_order or {}).get("finalizedAt") or self._now_iso()

        return {
            **order,
            "deliveryConfirmed": completion["deliveryConfirmed"],
            "paymentCompleted": completion["paymentCompleted"],
            "isFinalized": completion["canFinalize"],
            "finalizedAt": finalized_at,
        }

    def _create_activity_log(self, state: Dict[str, Any], action: str, entity_type: str, entity_id: str, description: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        log = {
            "id": self._next_record_id("LOG"),
            "timestamp": self._now_iso(),
            "action": action,
            "entityType": entity_type,
            "entityId": entity_id,
            "description": description,
            "metadata": metadata or {},
        }
        state["activity_logs"].insert(0, log)
        state["activity_logs"] = state["activity_logs"][:MAX_ACTIVITY_LOGS]
        return log

    def _create_alert(self, state: Dict[str, Any], code: str, severity: str, entity_type: str, entity_id: str, message: str, recipients: List[str], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        existing_active = next(
            (
                a
                for a in state["alerts"]
                if a.get("status") == "active"
                and a.get("code") == code
                and a.get("entityType") == entity_type
                and a.get("entityId") == entity_id
            ),
            None,
        )
        if existing_active:
            return existing_active

        alert = {
            "id": self._next_record_id("ALT"),
            "createdAt": self._now_iso(),
            "status": "active",
            "code": code,
            "severity": severity,
            "entityType": entity_type,
            "entityId": entity_id,
            "message": message,
            "recipients": recipients,
            "metadata": metadata or {},
        }
        state["alerts"].insert(0, alert)

        for recipient in recipients:
            state["notifications"].insert(
                0,
                {
                    "id": self._next_record_id("NTF"),
                    "createdAt": self._now_iso(),
                    "recipient": recipient,
                    "alertId": alert["id"],
                    "message": f"[{severity.upper()}] {message}",
                    "read": False,
                },
            )

        self._create_activity_log(
            state,
            "DISCREPANCY_ALERT_CREATED",
            entity_type,
            entity_id,
            message,
            {"code": code, "severity": severity, "recipients": recipients},
        )
        return alert

    def _resolve_alert_by_code(self, state: Dict[str, Any], entity_type: str, entity_id: str, code: str) -> None:
        for alert in state["alerts"]:
            if (
                alert.get("status") == "active"
                and alert.get("entityType") == entity_type
                and alert.get("entityId") == entity_id
                and alert.get("code") == code
            ):
                alert["status"] = "resolved"
                alert["resolvedAt"] = self._now_iso()

    def _sync_discrepancy_alerts(self, state: Dict[str, Any], entity_type: str, entity_id: str, issues: List[Dict[str, Any]], recipients: List[str]) -> None:
        issue_codes = {issue.get("code") for issue in issues}

        for issue in issues:
            self._create_alert(
                state,
                issue.get("code"),
                issue.get("severity", "medium"),
                entity_type,
                entity_id,
                issue.get("message", "Discrepancy detected"),
                recipients,
                issue.get("metadata") or {},
            )

        for alert in state["alerts"]:
            if (
                alert.get("status") == "active"
                and alert.get("entityType") == entity_type
                and alert.get("entityId") == entity_id
                and alert.get("code") not in issue_codes
            ):
                self._resolve_alert_by_code(state, entity_type, entity_id, str(alert.get("code")))

    def _get_order_discrepancies(self, order: Dict[str, Any], products_by_id: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        items = order.get("items") or []

        if not items:
            issues.append({"code": "ORDER_EMPTY_ITEMS", "severity": "high", "message": f"Order {order.get('id')} has no line items."})

        has_invalid_item_data = False
        for idx, item in enumerate(items):
            qty = float(item.get("qty", 0) or 0)
            price = float(item.get("price", 0) or 0)
            if qty <= 0 or price < 0:
                has_invalid_item_data = True

            product = products_by_id.get(str(item.get("productId")))
            if product and float(product.get("stock", 0) or 0) < qty:
                issues.append(
                    {
                        "code": f"ORDER_STOCK_MISMATCH_{item.get('productId')}",
                        "severity": "medium",
                        "message": f"Order {order.get('id')} requests {qty} units of {item.get('name') or item.get('productId')}, but stock is {product.get('stock')}.",
                        "metadata": {
                            "itemIndex": idx,
                            "productId": item.get("productId"),
                            "requested": qty,
                            "stock": product.get("stock"),
                        },
                    }
                )

        if has_invalid_item_data:
            issues.append(
                {
                    "code": "ORDER_INVALID_ITEM_DATA",
                    "severity": "high",
                    "message": f"Order {order.get('id')} contains invalid quantity or price values.",
                }
            )

        expected_total = self._calculate_order_expected_total(order)
        total = float(order.get("total", 0) or 0)
        if abs(expected_total - total) > 0.01:
            issues.append(
                {
                    "code": "ORDER_TOTAL_MISMATCH",
                    "severity": "high",
                    "message": f"Order {order.get('id')} total ({total}) does not match items total ({expected_total}).",
                    "metadata": {"expectedTotal": expected_total, "total": total},
                }
            )

        if order.get("status") == "Delivered" and order.get("payment") != "Paid":
            issues.append(
                {
                    "code": "ORDER_DELIVERED_UNPAID",
                    "severity": "medium",
                    "message": f"Order {order.get('id')} is delivered but payment is not completed.",
                }
            )

        return issues

    def _get_inventory_discrepancies(self, product: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        stock = float(product.get("stock", 0) or 0)

        if stock < 0:
            issues.append(
                {
                    "code": "INVENTORY_NEGATIVE_STOCK",
                    "severity": "high",
                    "message": f"Product {product.get('name')} has negative stock ({stock}).",
                }
            )

        if product.get("price") is not None and float(product.get("price") or 0) < 0:
            issues.append(
                {
                    "code": "INVENTORY_NEGATIVE_PRICE",
                    "severity": "high",
                    "message": f"Product {product.get('name')} has a negative price.",
                }
            )

        return issues

    def _run_discrepancy_checks_for_product(self, state: Dict[str, Any], product: Dict[str, Any]) -> None:
        issues = self._get_inventory_discrepancies(product)
        self._sync_discrepancy_alerts(state, "product", str(product.get("id")), issues, ["warehouse_manager"])

    def _run_discrepancy_checks_for_order(self, state: Dict[str, Any], order: Dict[str, Any]) -> None:
        products_by_id = {str(p.get("id")): p for p in state["products"]}
        issues = self._get_order_discrepancies(order, products_by_id)
        self._sync_discrepancy_alerts(
            state,
            "order",
            str(order.get("id")),
            issues,
            ["warehouse_manager", "order_fulfillment_specialist"],
        )

    def _run_global_discrepancy_checks(self, state: Dict[str, Any]) -> None:
        for product in state["products"]:
            self._run_discrepancy_checks_for_product(state, product)
        for order in state["orders"]:
            self._run_discrepancy_checks_for_order(state, order)

    def get_products(self) -> List[Dict[str, Any]]:
        state = self._load_state()
        return state["products"]

    def add_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        state = self._load_state()
        product = deepcopy(product)
        product["id"] = self._next_id("P", state["products"])
        state["products"].append(product)

        self._create_activity_log(
            state,
            "STOCK_UPDATED",
            "product",
            product["id"],
            f"Product {product.get('name')} created with stock {product.get('stock')}",
            {"stock": product.get("stock"), "sku": product.get("sku")},
        )
        self._run_discrepancy_checks_for_product(state, product)
        self._save_state(state)
        return product

    def update_product(self, product_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        state = self._load_state()
        idx = next((i for i, p in enumerate(state["products"]) if str(p.get("id")) == str(product_id)), -1)
        if idx == -1:
            return None

        previous = deepcopy(state["products"][idx])
        state["products"][idx].update(updates)

        if "stock" in updates and float(previous.get("stock", 0) or 0) != float(state["products"][idx].get("stock", 0) or 0):
            self._create_activity_log(
                state,
                "STOCK_UPDATED",
                "product",
                str(product_id),
                f"Stock updated for {state['products'][idx].get('name')}: {previous.get('stock')} -> {state['products'][idx].get('stock')}",
                {"previousStock": previous.get("stock"), "updatedStock": state["products"][idx].get("stock")},
            )

        self._run_discrepancy_checks_for_product(state, state["products"][idx])
        self._save_state(state)
        return state["products"][idx]

    def delete_product(self, product_id: str) -> bool:
        state = self._load_state()
        before = len(state["products"])
        state["products"] = [p for p in state["products"] if str(p.get("id")) != str(product_id)]
        self._save_state(state)
        return len(state["products"]) < before

    def get_orders(self) -> List[Dict[str, Any]]:
        state = self._load_state()
        normalized: List[Dict[str, Any]] = []
        for order in state["orders"]:
            normalized.append(self._apply_order_completion_state(order, order))
        return normalized

    def add_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        state = self._load_state()
        order = deepcopy(order)
        order["id"] = self._next_id("ORD-", state["orders"])
        if not order.get("date"):
            order["date"] = datetime.utcnow().strftime("%Y-%m-%d")

        finalized_order = self._apply_order_completion_state(order)
        state["orders"].insert(0, finalized_order)

        self._create_activity_log(
            state,
            "ORDER_CREATED",
            "order",
            finalized_order["id"],
            f"Order {finalized_order['id']} created for {finalized_order.get('customer')}",
            {
                "total": finalized_order.get("total"),
                "status": finalized_order.get("status"),
                "payment": finalized_order.get("payment"),
            },
        )

        self._run_discrepancy_checks_for_order(state, finalized_order)
        self._save_state(state)
        return finalized_order

    def update_order(self, order_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        state = self._load_state()
        idx = next((i for i, o in enumerate(state["orders"]) if str(o.get("id")) == str(order_id)), -1)
        if idx == -1:
            return None

        previous = deepcopy(state["orders"][idx])
        merged = {**state["orders"][idx], **updates}
        state["orders"][idx] = self._apply_order_completion_state(merged, previous)

        if "status" in updates and previous.get("status") != state["orders"][idx].get("status"):
            action = "DELIVERY_CONFIRMED" if state["orders"][idx].get("status") == "Delivered" else "ORDER_STATUS_UPDATED"
            self._create_activity_log(
                state,
                action,
                "order",
                str(order_id),
                f"Order {order_id} status changed: {previous.get('status')} -> {state['orders'][idx].get('status')}",
                {"previousStatus": previous.get("status"), "updatedStatus": state["orders"][idx].get("status")},
            )

        if "payment" in updates and previous.get("payment") != state["orders"][idx].get("payment"):
            self._create_activity_log(
                state,
                "PAYMENT_UPDATED",
                "order",
                str(order_id),
                f"Order {order_id} payment changed: {previous.get('payment')} -> {state['orders'][idx].get('payment')}",
                {"previousPayment": previous.get("payment"), "updatedPayment": state["orders"][idx].get("payment")},
            )

        if not previous.get("isFinalized") and state["orders"][idx].get("isFinalized"):
            self._create_activity_log(
                state,
                "ORDER_FINALIZED",
                "order",
                str(order_id),
                f"Order {order_id} finalized after payment and delivery verification",
                {"finalizedAt": state["orders"][idx].get("finalizedAt")},
            )

        self._run_discrepancy_checks_for_order(state, state["orders"][idx])
        self._save_state(state)
        return state["orders"][idx]

    def verify_order_completion(self, order_id: str) -> Optional[Dict[str, Any]]:
        order = next((o for o in self.get_orders() if str(o.get("id")) == str(order_id)), None)
        if not order:
            return None
        completion = self._evaluate_order_completion(order)
        return {
            "orderId": order_id,
            "deliveryConfirmed": completion["deliveryConfirmed"],
            "paymentCompleted": completion["paymentCompleted"],
            "canFinalize": completion["canFinalize"],
            "finalizedAt": order.get("finalizedAt") if completion["canFinalize"] else None,
        }

    def get_activity_logs(self) -> List[Dict[str, Any]]:
        return self._load_state()["activity_logs"]

    def get_alerts(self) -> List[Dict[str, Any]]:
        return self._load_state()["alerts"]

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        return [a for a in self.get_alerts() if a.get("status") == "active"]

    def resolve_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        state = self._load_state()
        idx = next((i for i, a in enumerate(state["alerts"]) if str(a.get("id")) == str(alert_id)), -1)
        if idx == -1:
            return None
        if state["alerts"][idx].get("status") == "resolved":
            return state["alerts"][idx]

        state["alerts"][idx]["status"] = "resolved"
        state["alerts"][idx]["resolvedAt"] = self._now_iso()

        self._create_activity_log(
            state,
            "DISCREPANCY_ALERT_RESOLVED",
            state["alerts"][idx].get("entityType", "unknown"),
            str(state["alerts"][idx].get("entityId", "")),
            f"Alert resolved: {state['alerts'][idx].get('message')}",
            {"alertId": state["alerts"][idx].get("id"), "code": state["alerts"][idx].get("code")},
        )
        self._save_state(state)
        return state["alerts"][idx]

    def get_notifications(self) -> List[Dict[str, Any]]:
        return self._load_state()["notifications"]

    def get_notifications_for_recipient(self, recipient: str) -> List[Dict[str, Any]]:
        return [n for n in self.get_notifications() if n.get("recipient") == recipient]

    def validate_order_stock(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        products_by_id = {str(p.get("id")): p for p in self.get_products()}
        issues: List[Dict[str, Any]] = []

        for idx, item in enumerate(items or []):
            product_id = str(item.get("productId", ""))
            qty = float(item.get("qty", 0) or 0)
            product = products_by_id.get(product_id)

            if not product:
                issues.append(
                    {
                        "itemIndex": idx,
                        "productId": product_id,
                        "message": f"Product {product_id} not found.",
                    }
                )
                continue

            available_stock = float(product.get("stock", 0) or 0)
            if qty > available_stock:
                issues.append(
                    {
                        "itemIndex": idx,
                        "productId": product_id,
                        "productName": product.get("name"),
                        "requestedQty": qty,
                        "availableStock": available_stock,
                        "message": f"Insufficient stock for {product.get('name')}. Requested: {qty}, Available: {available_stock}",
                    }
                )

        return {"isValid": len(issues) == 0, "issues": issues}

    def adjust_stock(self, product_id: str, adjustment_qty: float, reason: str = "manual") -> Optional[Dict[str, Any]]:
        state = self._load_state()
        idx = next((i for i, p in enumerate(state["products"]) if str(p.get("id")) == str(product_id)), -1)
        if idx == -1:
            return None

        previous_stock = float(state["products"][idx].get("stock", 0) or 0)
        new_stock = max(0.0, previous_stock + float(adjustment_qty))
        state["products"][idx]["stock"] = new_stock

        adjustment = {
            "id": self._next_record_id("ADJ"),
            "productId": product_id,
            "productName": state["products"][idx].get("name"),
            "previousStock": previous_stock,
            "adjustmentQty": adjustment_qty,
            "newStock": new_stock,
            "reason": reason,
            "timestamp": self._now_iso(),
        }
        state["stock_adjustments"].insert(0, adjustment)

        self._create_activity_log(
            state,
            "STOCK_ADJUSTED",
            "product",
            product_id,
            f"Stock adjusted for {state['products'][idx].get('name')}: {previous_stock} -> {new_stock} ({reason})",
            {
                "previousStock": previous_stock,
                "adjustmentQty": adjustment_qty,
                "newStock": new_stock,
                "reason": reason,
                "adjustmentId": adjustment["id"],
            },
        )

        self._run_discrepancy_checks_for_product(state, state["products"][idx])
        self._save_state(state)
        return adjustment

    def dispatch_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        order = next((o for o in self.get_orders() if str(o.get("id")) == str(order_id)), None)
        if not order:
            return None

        for item in order.get("items") or []:
            self.adjust_stock(str(item.get("productId")), -float(item.get("qty", 0) or 0), f"order_dispatch_{order_id}")

        updated = self.update_order(order_id, {"status": "Shipped"})
        if updated:
            state = self._load_state()
            self._create_activity_log(
                state,
                "ORDER_DISPATCHED",
                "order",
                order_id,
                f"Order {order_id} dispatched. Inventory reduced for {len(order.get('items') or [])} product(s).",
                {"itemCount": len(order.get("items") or [])},
            )
            self._save_state(state)
        return updated

    def cancel_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        order = next((o for o in self.get_orders() if str(o.get("id")) == str(order_id)), None)
        if not order:
            return None

        for item in order.get("items") or []:
            self.adjust_stock(str(item.get("productId")), float(item.get("qty", 0) or 0), f"order_cancellation_{order_id}")

        updated = self.update_order(order_id, {"status": "Cancelled"})
        if updated:
            state = self._load_state()
            self._create_activity_log(
                state,
                "ORDER_CANCELLED",
                "order",
                order_id,
                f"Order {order_id} cancelled. Inventory restored for {len(order.get('items') or [])} product(s).",
                {"itemCount": len(order.get("items") or [])},
            )
            self._save_state(state)
        return updated

    def record_sample_distribution(self, product_id: str, quantity: float, recipient_type: str = "unknown") -> Optional[Dict[str, Any]]:
        state = self._load_state()
        product = next((p for p in state["products"] if str(p.get("id")) == str(product_id)), None)
        if not product:
            return None

        distribution = {
            "id": self._next_record_id("SAMP"),
            "productId": product_id,
            "productName": product.get("name"),
            "quantity": quantity,
            "recipientType": recipient_type,
            "recordedAt": self._now_iso(),
        }
        state["sample_distributions"].insert(0, distribution)
        self._save_state(state)

        self.adjust_stock(product_id, -float(quantity), f"sample_distribution_{recipient_type}")

        state = self._load_state()
        self._create_activity_log(
            state,
            "SAMPLE_DISTRIBUTION_RECORDED",
            "product",
            product_id,
            f"Sample distribution recorded: {quantity} units of {product.get('name')} given to {recipient_type}.",
            {"quantity": quantity, "recipientType": recipient_type, "distributionId": distribution["id"]},
        )
        self._save_state(state)
        return distribution

    def get_sample_distributions(self) -> List[Dict[str, Any]]:
        return self._load_state()["sample_distributions"]

    def record_physical_stock(self, product_id: str, physical_count: float) -> Optional[Dict[str, Any]]:
        state = self._load_state()
        product = next((p for p in state["products"] if str(p.get("id")) == str(product_id)), None)
        if not product:
            return None

        recorded_stock = float(product.get("stock", 0) or 0)
        physical = float(physical_count or 0)
        variance = physical - recorded_stock

        record = {
            "id": self._next_record_id("PSC"),
            "productId": product_id,
            "productName": product.get("name"),
            "recordedStock": recorded_stock,
            "physicalCount": physical,
            "variance": variance,
            "recordedAt": self._now_iso(),
        }
        state["physical_stocks"].insert(0, record)

        self._create_activity_log(
            state,
            "PHYSICAL_STOCK_RECORDED",
            "product",
            product_id,
            f"Physical count for {product.get('name')}: {physical} units (system: {recorded_stock}, variance: {variance:+})",
            {"recordedStock": recorded_stock, "physicalCount": physical, "variance": variance},
        )

        if variance != 0:
            self._create_alert(
                state,
                f"STOCK_MISMATCH_{product_id}",
                "high" if abs(variance) > 10 else "medium",
                "product",
                product_id,
                f"Stock mismatch for {product.get('name')}: system shows {recorded_stock}, physical count is {physical} ({variance:+})",
                ["warehouse_manager"],
                {"variance": variance, "record": record["id"]},
            )

        self._save_state(state)
        return record

    def get_physical_stock_records(self) -> List[Dict[str, Any]]:
        return self._load_state()["physical_stocks"]

    def get_stock_mismatches(self) -> List[Dict[str, Any]]:
        return [r for r in self.get_physical_stock_records() if float(r.get("variance", 0) or 0) != 0]

    def get_stock_adjustments(self) -> List[Dict[str, Any]]:
        return self._load_state()["stock_adjustments"]

    def get_pending_payment_orders(self) -> List[Dict[str, Any]]:
        return [o for o in self.get_orders() if o.get("payment") == "Unpaid"]

    def get_pending_payment_stats(self) -> Dict[str, Any]:
        pending = self.get_pending_payment_orders()
        total_amount = sum(float(o.get("total", 0) or 0) for o in pending)
        return {
            "count": len(pending),
            "totalAmount": total_amount,
            "orders": pending,
        }
