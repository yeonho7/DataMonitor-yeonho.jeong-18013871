from __future__ import annotations
import json
import pytest
from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository


@pytest.fixture
def sample_file(tmp_path):
    data = [
        {"sample_id": "S-001", "name": "웨이퍼", "avg_production_time": 0.5,
         "yield_rate": 0.9, "stock": 100},
        {"sample_id": "S-002", "name": "기판", "avg_production_time": 0.3,
         "yield_rate": 0.8, "stock": 50},
    ]
    p = tmp_path / "samples.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return str(p)


@pytest.fixture
def order_file(tmp_path):
    data = [
        {"order_id": "O-1", "sample_id": "S-001", "customer": "A",
         "quantity": 10, "status": "RESERVED", "created_at": "", "updated_at": ""},
        {"order_id": "O-2", "sample_id": "S-001", "customer": "B",
         "quantity": 20, "status": "CONFIRMED", "created_at": "", "updated_at": ""},
    ]
    p = tmp_path / "orders.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return str(p)


def test_sample_repo_find_all(sample_file):
    repo = SampleRepository(sample_file)
    samples = repo.find_all()
    assert len(samples) == 2
    assert samples[0].sample_id == "S-001"
    assert samples[1].stock == 50


def test_order_repo_find_all(order_file):
    repo = OrderRepository(order_file)
    orders = repo.find_all()
    assert len(orders) == 2


def test_order_repo_find_by_status(order_file):
    repo = OrderRepository(order_file)
    reserved = repo.find_by_status("RESERVED")
    assert len(reserved) == 1
    assert reserved[0].order_id == "O-1"


def test_order_repo_find_by_status_empty(order_file):
    repo = OrderRepository(order_file)
    assert repo.find_by_status("PRODUCING") == []


def test_sample_repo_missing_file(tmp_path):
    repo = SampleRepository(str(tmp_path / "no.json"))
    assert repo.find_all() == []


def test_order_repo_missing_file(tmp_path):
    repo = OrderRepository(str(tmp_path / "no.json"))
    assert repo.find_all() == []
