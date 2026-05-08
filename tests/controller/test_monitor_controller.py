import pytest
from model.sample import Sample
from model.order import Order
from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from controller.monitor_controller import MonitorController, StockStatus


@pytest.fixture
def repos(tmp_path):
    return (
        SampleRepository(str(tmp_path / "samples.json")),
        OrderRepository(str(tmp_path / "orders.json")),
    )


def test_get_summary(repos):
    sample_repo, order_repo = repos
    sample_repo.create(Sample("S-001", "웨이퍼", 0.5, 0.9, 100))
    sample_repo.create(Sample("S-002", "기판", 0.3, 0.8, 50))
    order_repo.create(Order("ORD-001", "S-001", "고객A", 30, "RESERVED"))
    order_repo.create(Order("ORD-002", "S-002", "고객B", 20, "CONFIRMED"))
    order_repo.create(Order("ORD-003", "S-001", "고객C", 10, "REJECTED"))

    ctrl = MonitorController(sample_repo, order_repo)
    summary = ctrl.get_summary()

    assert summary["sample_count"] == 2
    assert summary["total_stock"] == 150
    assert summary["total_orders"] == 2  # REJECTED 제외


def test_get_order_status_summary_excludes_rejected(repos):
    sample_repo, order_repo = repos
    order_repo.create(Order("ORD-001", "S-001", "고객A", 10, "RESERVED"))
    order_repo.create(Order("ORD-002", "S-001", "고객B", 20, "REJECTED"))
    order_repo.create(Order("ORD-003", "S-001", "고객C", 30, "RELEASED"))

    ctrl = MonitorController(sample_repo, order_repo)
    summary = ctrl.get_order_status_summary()

    assert "REJECTED" not in summary
    assert len(summary["RESERVED"]) == 1
    assert len(summary["RELEASED"]) == 1
    assert len(summary["PRODUCING"]) == 0
    assert len(summary["CONFIRMED"]) == 0


def test_stock_status_surplus(repos):
    sample_repo, order_repo = repos
    sample_repo.create(Sample("S-001", "웨이퍼", 0.5, 0.9, 500))
    order_repo.create(Order("ORD-001", "S-001", "고객A", 100, "RESERVED"))

    ctrl = MonitorController(sample_repo, order_repo)
    items = ctrl.get_stock_status()

    assert items[0]["stock_status"] == StockStatus.SURPLUS


def test_stock_status_short(repos):
    sample_repo, order_repo = repos
    sample_repo.create(Sample("S-001", "웨이퍼", 0.5, 0.9, 50))
    order_repo.create(Order("ORD-001", "S-001", "고객A", 100, "RESERVED"))

    ctrl = MonitorController(sample_repo, order_repo)
    items = ctrl.get_stock_status()

    assert items[0]["stock_status"] == StockStatus.SHORT


def test_stock_status_depleted(repos):
    sample_repo, order_repo = repos
    sample_repo.create(Sample("S-001", "웨이퍼", 0.5, 0.9, 0))

    ctrl = MonitorController(sample_repo, order_repo)
    items = ctrl.get_stock_status()

    assert items[0]["stock_status"] == StockStatus.DEPLETED


def test_remaining_pct_calculation(repos):
    sample_repo, order_repo = repos
    sample_repo.create(Sample("S-001", "웨이퍼", 0.5, 0.9, 80))
    order_repo.create(Order("ORD-001", "S-001", "고객A", 20, "RESERVED"))

    ctrl = MonitorController(sample_repo, order_repo)
    items = ctrl.get_stock_status()

    # 80 / (80 + 20) * 100 = 80.0
    assert items[0]["remaining_pct"] == 80.0


def test_remaining_pct_100_when_no_orders(repos):
    sample_repo, order_repo = repos
    sample_repo.create(Sample("S-001", "웨이퍼", 0.5, 0.9, 100))

    ctrl = MonitorController(sample_repo, order_repo)
    items = ctrl.get_stock_status()

    assert items[0]["remaining_pct"] == 100.0
