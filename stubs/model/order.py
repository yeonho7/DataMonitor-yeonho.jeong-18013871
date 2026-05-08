from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Order:
    order_id: str
    sample_id: str
    customer: str
    quantity: int
    status: str
    created_at: str = field(default="")
    updated_at: str = field(default="")
