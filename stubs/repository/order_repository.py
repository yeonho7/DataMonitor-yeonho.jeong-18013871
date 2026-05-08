from __future__ import annotations
import json
from model.order import Order


class OrderRepository:
    def __init__(self, path: str) -> None:
        self._path = path

    def find_all(self) -> list[Order]:
        try:
            with open(self._path, encoding="utf-8") as f:
                rows = json.load(f)
        except FileNotFoundError:
            return []
        return [Order(**r) for r in rows]

    def find_by_status(self, status: str) -> list[Order]:
        return [o for o in self.find_all() if o.status == status]
