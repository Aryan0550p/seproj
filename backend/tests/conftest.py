from pathlib import Path
import sys
import uuid

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import app as app_module
from services.store_service import StoreService


@pytest.fixture()
def store(monkeypatch):
    temp_root = BACKEND_DIR / ".test_tmp"
    temp_root.mkdir(exist_ok=True)

    unique_id = uuid.uuid4().hex
    data_file = temp_root / f"data_{unique_id}.json"
    db_file = temp_root / f"yumsie_test_{unique_id}.db"
    test_store = StoreService(data_file=str(data_file), db_file=str(db_file))
    monkeypatch.setattr(app_module, "store", test_store)
    yield test_store
    for path in (data_file, db_file):
        try:
            path.unlink()
        except (FileNotFoundError, PermissionError):
            pass


@pytest.fixture()
def client(store):
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def seed_products(client):
    return client.get("/api/products").get_json()


@pytest.fixture()
def seed_orders(client):
    return client.get("/api/orders").get_json()


@pytest.fixture()
def valid_order_payload():
    return {
        "customer": "QA Retail Partner",
        "createdBy": "tester",
        "items": [
            {
                "productId": "P001",
                "name": "Premium Coffee Beans",
                "qty": 2,
                "price": 1200,
            }
        ],
        "total": 2400,
        "status": "Pending",
        "payment": "Unpaid",
    }
