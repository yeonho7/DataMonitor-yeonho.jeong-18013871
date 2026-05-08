# DataMonitor POC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 반도체 시료 생산주문관리 시스템의 데이터 상태를 콘솔에서 실시간 조회하는 관리자 도구(DataMonitor POC)를 구현한다.

**Architecture:** MVC 패턴으로 구성. Model(도메인 모델) → Repository(JSON 영속성) → Controller(비즈니스 로직) → View(콘솔 출력) 순서로 계층이 단방향 의존한다. 데이터는 `data/*.json` 파일에 저장한다.

**Tech Stack:** Python 3.x, 표준 라이브러리(json, dataclasses, enum), pytest(테스트)

---

## 파일 구조

```
DataMonitor/
├── data/
│   ├── samples.json              # 시료 시드 데이터
│   └── orders.json               # 주문 시드 데이터
├── model/
│   ├── __init__.py
│   ├── sample.py                 # Sample 도메인 모델
│   └── order.py                  # Order 도메인 모델 + OrderStatus Enum
├── repository/
│   ├── __init__.py
│   ├── sample_repository.py      # 시료 CRUD (JSON I/O)
│   └── order_repository.py       # 주문 CRUD (JSON I/O)
├── controller/
│   ├── __init__.py
│   └── monitor_controller.py     # 모니터링 비즈니스 로직
├── view/
│   ├── __init__.py
│   └── monitor_view.py           # 콘솔 출력 및 입력
├── tests/
│   ├── __init__.py
│   ├── model/
│   │   ├── __init__.py
│   │   ├── test_sample.py
│   │   └── test_order.py
│   ├── repository/
│   │   ├── __init__.py
│   │   ├── test_sample_repository.py
│   │   └── test_order_repository.py
│   └── controller/
│       ├── __init__.py
│       └── test_monitor_controller.py
├── docs/
│   ├── PRD.md
│   └── PLAN.md
└── main.py
```

---

## Task 1: 개발 환경 준비

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/model/__init__.py`
- Create: `tests/repository/__init__.py`
- Create: `tests/controller/__init__.py`

- [ ] **Step 1: pytest 설치 확인**

```bash
.venv\Scripts\pip install pytest
```

Expected: `Successfully installed pytest-...` 또는 `Requirement already satisfied`

- [ ] **Step 2: 패키지 __init__.py 파일 생성**

아래 파일들을 빈 파일로 생성한다:
- `model/__init__.py`
- `repository/__init__.py`
- `controller/__init__.py`
- `view/__init__.py`
- `tests/__init__.py`
- `tests/model/__init__.py`
- `tests/repository/__init__.py`
- `tests/controller/__init__.py`

- [ ] **Step 3: pytest 동작 확인**

```bash
.venv\Scripts\pytest tests/ -v
```

Expected: `no tests ran` (아직 테스트 없음)

- [ ] **Step 4: Commit**

```bash
git add model/__init__.py repository/__init__.py controller/__init__.py view/__init__.py tests/
git commit -m "chore: 프로젝트 패키지 구조 초기화"
```

---

## Task 2: 도메인 모델 (Sample, Order)

**Files:**
- Create: `model/sample.py`
- Create: `model/order.py`
- Create: `tests/model/test_sample.py`
- Create: `tests/model/test_order.py`

- [ ] **Step 1: 실패하는 Sample 테스트 작성**

`tests/model/test_sample.py`:
```python
from model.sample import Sample


def test_sample_to_dict():
    sample = Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    assert sample.to_dict() == {
        "sample_id": "S-001",
        "name": "실리콘 웨이퍼-8인치",
        "avg_production_time": 0.5,
        "yield_rate": 0.92,
        "stock": 480,
    }


def test_sample_from_dict():
    d = {
        "sample_id": "S-001",
        "name": "실리콘 웨이퍼-8인치",
        "avg_production_time": 0.5,
        "yield_rate": 0.92,
        "stock": 480,
    }
    sample = Sample.from_dict(d)
    assert sample.sample_id == "S-001"
    assert sample.stock == 480


def test_sample_roundtrip():
    original = Sample("S-002", "GaN 에피택셜-4인치", 0.3, 0.78, 220)
    assert Sample.from_dict(original.to_dict()) == original
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
.venv\Scripts\pytest tests/model/test_sample.py -v
```

Expected: `FAILED` — `ModuleNotFoundError: No module named 'model.sample'`

- [ ] **Step 3: Sample 모델 구현**

`model/sample.py`:
```python
from __future__ import annotations
from dataclasses import dataclass, asdict


@dataclass
class Sample:
    sample_id: str
    name: str
    avg_production_time: float
    yield_rate: float
    stock: int

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Sample:
        return cls(
            sample_id=data["sample_id"],
            name=data["name"],
            avg_production_time=data["avg_production_time"],
            yield_rate=data["yield_rate"],
            stock=data["stock"],
        )
```

- [ ] **Step 4: Sample 테스트 통과 확인**

```bash
.venv\Scripts\pytest tests/model/test_sample.py -v
```

Expected: `3 passed`

- [ ] **Step 5: 실패하는 Order 테스트 작성**

`tests/model/test_order.py`:
```python
from model.order import Order, OrderStatus


def test_order_to_dict_serializes_status_as_string():
    order = Order("ORD-001", "S-001", "SK하이닉스", 100, OrderStatus.RESERVED)
    d = order.to_dict()
    assert d["status"] == "RESERVED"


def test_order_from_dict_parses_status_enum():
    d = {
        "order_id": "ORD-001",
        "sample_id": "S-001",
        "customer": "SK하이닉스",
        "quantity": 100,
        "status": "PRODUCING",
    }
    order = Order.from_dict(d)
    assert order.status == OrderStatus.PRODUCING


def test_order_roundtrip():
    original = Order("ORD-002", "S-003", "삼성전자", 200, OrderStatus.CONFIRMED)
    assert Order.from_dict(original.to_dict()) == original
```

- [ ] **Step 6: 테스트 실패 확인**

```bash
.venv\Scripts\pytest tests/model/test_order.py -v
```

Expected: `FAILED` — `ModuleNotFoundError: No module named 'model.order'`

- [ ] **Step 7: Order 모델 구현**

`model/order.py`:
```python
from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum


class OrderStatus(Enum):
    RESERVED = "RESERVED"
    REJECTED = "REJECTED"
    PRODUCING = "PRODUCING"
    CONFIRMED = "CONFIRMED"
    RELEASED = "RELEASED"


MONITORED_STATUSES = [
    OrderStatus.RESERVED,
    OrderStatus.PRODUCING,
    OrderStatus.CONFIRMED,
    OrderStatus.RELEASED,
]

ACTIVE_STATUSES = [
    OrderStatus.RESERVED,
    OrderStatus.PRODUCING,
    OrderStatus.CONFIRMED,
]


@dataclass
class Order:
    order_id: str
    sample_id: str
    customer: str
    quantity: int
    status: OrderStatus

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, data: dict) -> Order:
        return cls(
            order_id=data["order_id"],
            sample_id=data["sample_id"],
            customer=data["customer"],
            quantity=data["quantity"],
            status=OrderStatus(data["status"]),
        )
```

- [ ] **Step 8: Order 테스트 통과 확인**

```bash
.venv\Scripts\pytest tests/model/ -v
```

Expected: `6 passed`

- [ ] **Step 9: Commit**

```bash
git add model/ tests/model/
git commit -m "feat: Sample, Order 도메인 모델 구현"
```

---

## Task 3: JSON Repository

**Files:**
- Create: `repository/sample_repository.py`
- Create: `repository/order_repository.py`
- Create: `tests/repository/test_sample_repository.py`
- Create: `tests/repository/test_order_repository.py`

- [ ] **Step 1: 실패하는 SampleRepository 테스트 작성**

`tests/repository/test_sample_repository.py`:
```python
import pytest
from model.sample import Sample
from repository.sample_repository import SampleRepository


@pytest.fixture
def tmp_json(tmp_path):
    return str(tmp_path / "samples.json")


def test_find_all_returns_empty_when_no_file(tmp_json):
    repo = SampleRepository(tmp_json)
    assert repo.find_all() == []


def test_save_and_find_all(tmp_json):
    repo = SampleRepository(tmp_json)
    sample = Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    repo.save(sample)
    assert repo.find_all() == [sample]


def test_find_by_id(tmp_json):
    repo = SampleRepository(tmp_json)
    sample = Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480)
    repo.save(sample)
    assert repo.find_by_id("S-001") == sample
    assert repo.find_by_id("S-999") is None


def test_save_persists_to_file(tmp_json):
    repo = SampleRepository(tmp_json)
    repo.save(Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480))
    repo2 = SampleRepository(tmp_json)
    assert repo2.find_by_id("S-001").stock == 480


def test_save_overwrites_existing(tmp_json):
    repo = SampleRepository(tmp_json)
    repo.save(Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480))
    repo.save(Sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 999))
    assert repo.find_by_id("S-001").stock == 999
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
.venv\Scripts\pytest tests/repository/test_sample_repository.py -v
```

Expected: `FAILED` — `ModuleNotFoundError: No module named 'repository.sample_repository'`

- [ ] **Step 3: SampleRepository 구현**

`repository/sample_repository.py`:
```python
from __future__ import annotations
import json
import os
from model.sample import Sample


class SampleRepository:
    def __init__(self, filepath: str):
        self._filepath = filepath
        self._samples: dict[str, Sample] = {}
        self._load()

    def find_all(self) -> list[Sample]:
        return list(self._samples.values())

    def find_by_id(self, sample_id: str) -> Sample | None:
        return self._samples.get(sample_id)

    def save(self, sample: Sample) -> None:
        self._samples[sample.sample_id] = sample
        self._persist()

    def _load(self) -> None:
        if not os.path.exists(self._filepath):
            return
        with open(self._filepath, encoding="utf-8") as f:
            for item in json.load(f):
                s = Sample.from_dict(item)
                self._samples[s.sample_id] = s

    def _persist(self) -> None:
        os.makedirs(os.path.dirname(self._filepath) or ".", exist_ok=True)
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(
                [s.to_dict() for s in self._samples.values()],
                f,
                ensure_ascii=False,
                indent=2,
            )
```

- [ ] **Step 4: SampleRepository 테스트 통과 확인**

```bash
.venv\Scripts\pytest tests/repository/test_sample_repository.py -v
```

Expected: `5 passed`

- [ ] **Step 5: 실패하는 OrderRepository 테스트 작성**

`tests/repository/test_order_repository.py`:
```python
import pytest
from model.order import Order, OrderStatus
from repository.order_repository import OrderRepository


@pytest.fixture
def tmp_json(tmp_path):
    return str(tmp_path / "orders.json")


def test_find_all_empty_on_missing_file(tmp_json):
    repo = OrderRepository(tmp_json)
    assert repo.find_all() == []


def test_save_and_find_by_status(tmp_json):
    repo = OrderRepository(tmp_json)
    o1 = Order("ORD-001", "S-001", "SK하이닉스", 100, OrderStatus.RESERVED)
    o2 = Order("ORD-002", "S-001", "LG이노텍", 200, OrderStatus.CONFIRMED)
    repo.save(o1)
    repo.save(o2)
    assert repo.find_by_status(OrderStatus.RESERVED) == [o1]
    assert repo.find_by_status(OrderStatus.CONFIRMED) == [o2]
    assert repo.find_by_status(OrderStatus.PRODUCING) == []


def test_save_persists_to_file(tmp_json):
    repo = OrderRepository(tmp_json)
    order = Order("ORD-001", "S-001", "SK하이닉스", 100, OrderStatus.PRODUCING)
    repo.save(order)
    repo2 = OrderRepository(tmp_json)
    found = repo2.find_by_status(OrderStatus.PRODUCING)
    assert len(found) == 1
    assert found[0].order_id == "ORD-001"
```

- [ ] **Step 6: 테스트 실패 확인**

```bash
.venv\Scripts\pytest tests/repository/test_order_repository.py -v
```

Expected: `FAILED` — `ModuleNotFoundError: No module named 'repository.order_repository'`

- [ ] **Step 7: OrderRepository 구현**

`repository/order_repository.py`:
```python
from __future__ import annotations
import json
import os
from model.order import Order, OrderStatus


class OrderRepository:
    def __init__(self, filepath: str):
        self._filepath = filepath
        self._orders: dict[str, Order] = {}
        self._load()

    def find_all(self) -> list[Order]:
        return list(self._orders.values())

    def find_by_status(self, status: OrderStatus) -> list[Order]:
        return [o for o in self._orders.values() if o.status == status]

    def save(self, order: Order) -> None:
        self._orders[order.order_id] = order
        self._persist()

    def _load(self) -> None:
        if not os.path.exists(self._filepath):
            return
        with open(self._filepath, encoding="utf-8") as f:
            for item in json.load(f):
                o = Order.from_dict(item)
                self._orders[o.order_id] = o

    def _persist(self) -> None:
        os.makedirs(os.path.dirname(self._filepath) or ".", exist_ok=True)
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(
                [o.to_dict() for o in self._orders.values()],
                f,
                ensure_ascii=False,
                indent=2,
            )
```

- [ ] **Step 8: 전체 Repository 테스트 통과 확인**

```bash
.venv\Scripts\pytest tests/repository/ -v
```

Expected: `8 passed`

- [ ] **Step 9: Commit**

```bash
git add repository/ tests/repository/
git commit -m "feat: SampleRepository, OrderRepository JSON 영속성 구현"
```

---

## Task 4: MonitorController (비즈니스 로직)

**Files:**
- Create: `controller/monitor_controller.py`
- Create: `tests/controller/test_monitor_controller.py`

- [ ] **Step 1: 실패하는 MonitorController 테스트 작성**

`tests/controller/test_monitor_controller.py`:
```python
import pytest
from model.sample import Sample
from model.order import Order, OrderStatus
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
    sample_repo.save(Sample("S-001", "웨이퍼", 0.5, 0.9, 100))
    sample_repo.save(Sample("S-002", "기판", 0.3, 0.8, 50))
    order_repo.save(Order("ORD-001", "S-001", "고객A", 30, OrderStatus.RESERVED))
    order_repo.save(Order("ORD-002", "S-002", "고객B", 20, OrderStatus.CONFIRMED))
    order_repo.save(Order("ORD-003", "S-001", "고객C", 10, OrderStatus.REJECTED))

    ctrl = MonitorController(sample_repo, order_repo)
    summary = ctrl.get_summary()

    assert summary["sample_count"] == 2
    assert summary["total_stock"] == 150
    assert summary["total_orders"] == 2  # REJECTED 제외


def test_get_order_status_summary_excludes_rejected(repos):
    sample_repo, order_repo = repos
    order_repo.save(Order("ORD-001", "S-001", "고객A", 10, OrderStatus.RESERVED))
    order_repo.save(Order("ORD-002", "S-001", "고객B", 20, OrderStatus.REJECTED))
    order_repo.save(Order("ORD-003", "S-001", "고객C", 30, OrderStatus.RELEASED))

    ctrl = MonitorController(sample_repo, order_repo)
    summary = ctrl.get_order_status_summary()

    assert "REJECTED" not in summary
    assert len(summary["RESERVED"]) == 1
    assert len(summary["RELEASED"]) == 1
    assert len(summary["PRODUCING"]) == 0
    assert len(summary["CONFIRMED"]) == 0


def test_stock_status_surplus(repos):
    sample_repo, order_repo = repos
    sample_repo.save(Sample("S-001", "웨이퍼", 0.5, 0.9, 500))
    order_repo.save(Order("ORD-001", "S-001", "고객A", 100, OrderStatus.RESERVED))

    ctrl = MonitorController(sample_repo, order_repo)
    items = ctrl.get_stock_status()

    assert items[0]["stock_status"] == StockStatus.SURPLUS


def test_stock_status_short(repos):
    sample_repo, order_repo = repos
    sample_repo.save(Sample("S-001", "웨이퍼", 0.5, 0.9, 50))
    order_repo.save(Order("ORD-001", "S-001", "고객A", 100, OrderStatus.RESERVED))

    ctrl = MonitorController(sample_repo, order_repo)
    items = ctrl.get_stock_status()

    assert items[0]["stock_status"] == StockStatus.SHORT


def test_stock_status_depleted(repos):
    sample_repo, order_repo = repos
    sample_repo.save(Sample("S-001", "웨이퍼", 0.5, 0.9, 0))

    ctrl = MonitorController(sample_repo, order_repo)
    items = ctrl.get_stock_status()

    assert items[0]["stock_status"] == StockStatus.DEPLETED


def test_remaining_pct_calculation(repos):
    sample_repo, order_repo = repos
    sample_repo.save(Sample("S-001", "웨이퍼", 0.5, 0.9, 80))
    order_repo.save(Order("ORD-001", "S-001", "고객A", 20, OrderStatus.RESERVED))

    ctrl = MonitorController(sample_repo, order_repo)
    items = ctrl.get_stock_status()

    # 80 / (80 + 20) * 100 = 80.0
    assert items[0]["remaining_pct"] == 80.0


def test_remaining_pct_100_when_no_orders(repos):
    sample_repo, order_repo = repos
    sample_repo.save(Sample("S-001", "웨이퍼", 0.5, 0.9, 100))

    ctrl = MonitorController(sample_repo, order_repo)
    items = ctrl.get_stock_status()

    assert items[0]["remaining_pct"] == 100.0
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
.venv\Scripts\pytest tests/controller/test_monitor_controller.py -v
```

Expected: `FAILED` — `ModuleNotFoundError: No module named 'controller.monitor_controller'`

- [ ] **Step 3: MonitorController 구현**

`controller/monitor_controller.py`:
```python
from __future__ import annotations
from model.order import Order, OrderStatus, MONITORED_STATUSES, ACTIVE_STATUSES
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
        active_orders = [
            o for o in self._order_repo.find_all() if o.status in MONITORED_STATUSES
        ]
        return {
            "sample_count": len(samples),
            "total_stock": sum(s.stock for s in samples),
            "total_orders": len(active_orders),
        }

    def get_order_status_summary(self) -> dict[str, list[Order]]:
        return {
            status.value: self._order_repo.find_by_status(status)
            for status in MONITORED_STATUSES
        }

    def get_stock_status(self) -> list[dict]:
        samples = self._sample_repo.find_all()
        active_orders = [
            o for o in self._order_repo.find_all() if o.status in ACTIVE_STATUSES
        ]
        result = []
        for sample in samples:
            active_qty = sum(
                o.quantity for o in active_orders if o.sample_id == sample.sample_id
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
```

- [ ] **Step 4: 전체 테스트 통과 확인**

```bash
.venv\Scripts\pytest tests/ -v
```

Expected: `21 passed`

- [ ] **Step 5: Commit**

```bash
git add controller/ tests/controller/
git commit -m "feat: MonitorController 비즈니스 로직 구현"
```

---

## Task 5: View + Main + 시드 데이터

**Files:**
- Create: `view/monitor_view.py`
- Create: `main.py`
- Create: `data/samples.json`
- Create: `data/orders.json`

- [ ] **Step 1: MonitorView 구현**

`view/monitor_view.py`:
```python
from __future__ import annotations


class MonitorView:
    def display_main_menu(self, summary: dict) -> None:
        print("\n" + "=" * 62)
        print("     DataMonitor  반도체 시료 생산주문관리 모니터링 도구")
        print("=" * 62)
        print(
            f"  등록 시료 {summary['sample_count']:>3}종   "
            f"총 재고 {summary['total_stock']:>6,} ea   "
            f"전체 주문 {summary['total_orders']:>3}건"
        )
        print("-" * 62)
        print("  [1] 주문량 확인")
        print("  [2] 재고량 확인")
        print("  [0] 종료")
        print("-" * 62)

    def display_order_summary(self, order_summary: dict) -> None:
        print("\n  ── 주문 현황 ──────────────────────────────────────────")
        total = 0
        for status_name, orders in order_summary.items():
            count = len(orders)
            total += count
            print(f"  {status_name:<12}: {count}건")
            for o in orders:
                print(
                    f"    · {o.order_id}  고객: {o.customer:<18}  수량: {o.quantity:>5} ea"
                )
        print(f"  {'합계':<12}: {total}건")
        print("  " + "─" * 58)

    def display_stock_status(self, stock_items: list[dict]) -> None:
        print("\n  ── 재고 현황 ──────────────────────────────────────────")
        print(f"  {'시료명':<22} {'재고':>7} {'활성주문':>8} {'상태':>6} {'잔여율':>7}")
        print("  " + "─" * 58)
        for item in stock_items:
            s = item["sample"]
            label = f"[{item['stock_status']}]"
            print(
                f"  {s.name:<22} {s.stock:>5} ea {item['active_order_qty']:>6} ea"
                f" {label:>7} {item['remaining_pct']:>6.1f}%"
            )
        print("  " + "─" * 58)

    def get_menu_input(self, prompt: str = "선택 > ") -> str:
        return input(prompt).strip()

    def display_message(self, message: str) -> None:
        print(f"  {message}")
```

- [ ] **Step 2: 시드 데이터 생성**

`data/samples.json`:
```json
[
  {
    "sample_id": "S-001",
    "name": "실리콘 웨이퍼-8인치",
    "avg_production_time": 0.5,
    "yield_rate": 0.92,
    "stock": 480
  },
  {
    "sample_id": "S-002",
    "name": "GaN 에피택셜-4인치",
    "avg_production_time": 0.3,
    "yield_rate": 0.78,
    "stock": 220
  },
  {
    "sample_id": "S-003",
    "name": "SiC 파워기판-6인치",
    "avg_production_time": 0.8,
    "yield_rate": 0.92,
    "stock": 30
  },
  {
    "sample_id": "S-004",
    "name": "포토레지스트-PR7",
    "avg_production_time": 0.2,
    "yield_rate": 0.95,
    "stock": 910
  },
  {
    "sample_id": "S-005",
    "name": "산화막 웨이퍼-SiO2",
    "avg_production_time": 0.6,
    "yield_rate": 0.88,
    "stock": 0
  }
]
```

`data/orders.json`:
```json
[
  {
    "order_id": "ORD-20260508-0001",
    "sample_id": "S-001",
    "customer": "SK하이닉스",
    "quantity": 150,
    "status": "RESERVED"
  },
  {
    "order_id": "ORD-20260508-0002",
    "sample_id": "S-003",
    "customer": "삼성전자 파운드리",
    "quantity": 200,
    "status": "PRODUCING"
  },
  {
    "order_id": "ORD-20260508-0003",
    "sample_id": "S-001",
    "customer": "LG이노텍",
    "quantity": 300,
    "status": "CONFIRMED"
  },
  {
    "order_id": "ORD-20260508-0004",
    "sample_id": "S-004",
    "customer": "DB하이텍",
    "quantity": 400,
    "status": "RELEASED"
  },
  {
    "order_id": "ORD-20260508-0005",
    "sample_id": "S-002",
    "customer": "네패스",
    "quantity": 100,
    "status": "REJECTED"
  }
]
```

- [ ] **Step 3: main.py 구현**

`main.py`:
```python
from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from controller.monitor_controller import MonitorController
from view.monitor_view import MonitorView

DATA_SAMPLES = "data/samples.json"
DATA_ORDERS = "data/orders.json"


def main() -> None:
    sample_repo = SampleRepository(DATA_SAMPLES)
    order_repo = OrderRepository(DATA_ORDERS)
    controller = MonitorController(sample_repo, order_repo)
    view = MonitorView()

    while True:
        summary = controller.get_summary()
        view.display_main_menu(summary)
        choice = view.get_menu_input()

        if choice == "1":
            view.display_order_summary(controller.get_order_status_summary())
        elif choice == "2":
            view.display_stock_status(controller.get_stock_status())
        elif choice == "0":
            view.display_message("종료합니다.")
            break
        else:
            view.display_message("올바른 메뉴를 선택하세요. (0/1/2)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 전체 테스트 통과 확인**

```bash
.venv\Scripts\pytest tests/ -v
```

Expected: `21 passed`

- [ ] **Step 5: 애플리케이션 수동 실행 확인**

```bash
.venv\Scripts\python main.py
```

확인 항목:
- 메인 메뉴에 `등록 시료 5종`, `총 재고 1,640 ea`, `전체 주문 4건` 표시
- [1] 선택 시 RESERVED 1건, PRODUCING 1건, CONFIRMED 1건, RELEASED 1건 표시 (REJECTED 미포함)
- [2] 선택 시 SiC 파워기판-6인치 `[부족]`, 산화막 웨이퍼-SiO2 `[고갈]` 표시

- [ ] **Step 6: Commit**

```bash
git add view/ main.py data/
git commit -m "feat: MonitorView, main 진입점, 시드 데이터 추가"
```

---

## 검증 체크리스트

```bash
# 전체 테스트
.venv\Scripts\pytest tests/ -v

# 실행
.venv\Scripts\python main.py
```

- [ ] 21개 테스트 전체 통과
- [ ] 메인 화면에 시료 수 / 총 재고 / 주문 수 표시
- [ ] [1] 주문량 확인: RESERVED/PRODUCING/CONFIRMED/RELEASED 건수 및 목록, REJECTED 미포함
- [ ] [2] 재고량 확인: 시료별 재고 + 여유/부족/고갈 상태 + 잔여율
- [ ] `data/*.json` 수정 후 재실행 시 변경 내용 반영
- [ ] Model / Repository / Controller / View 패키지 명확히 분리
