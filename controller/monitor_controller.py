from __future__ import annotations
import config  # noqa: F401  — DataPersistence/ 를 sys.path에 추가
from config import MONITORED_STATUSES, ACTIVE_STATUSES
from model.order import Order
from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository


class StockStatus:
    SURPLUS = "여유"
    SHORT = "부족"
    DEPLETED = "고갈"


class MonitorController:
    def __init__(self, sample_repo: SampleRepository, order_repo: OrderRepository):
        self._sample_repo = sample_repo
        self._order_repo = order_repo

    def get_summary(self) -> dict:
        samples = self._sample_repo.find_all()
        monitored_orders = [
            o for o in self._order_repo.find_all()
            if o.status in MONITORED_STATUSES
        ]
        return {
            "sample_count": len(samples),
            "total_stock": sum(s.stock for s in samples),
            "total_orders": len(monitored_orders),
        }

    def get_order_status_summary(self) -> dict[str, list[Order]]:
        return {
            status: self._order_repo.find_by_status(status)
            for status in MONITORED_STATUSES
        }

    def get_stock_status(self) -> list[dict]:
        samples = self._sample_repo.find_all()
        active_orders = [
            o for o in self._order_repo.find_all()
            if o.status in ACTIVE_STATUSES
        ]
        result = []
        for sample in samples:
            active_qty = sum(
                o.quantity for o in active_orders
                if o.sample_id == sample.sample_id
            )
            if sample.stock == 0:
                status = StockStatus.DEPLETED
            elif sample.stock < active_qty:
                status = StockStatus.SHORT
            else:
                status = StockStatus.SURPLUS

            total = sample.stock + active_qty
            remaining_pct = (sample.stock / total * 100) if total > 0 else 100.0

            result.append({
                "sample": sample,
                "active_order_qty": active_qty,
                "stock_status": status,
                "remaining_pct": remaining_pct,
            })
        return result
