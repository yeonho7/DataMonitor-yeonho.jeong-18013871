# DataMonitor 서브모듈 통합 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** DataPersistence, DummyDataGenerator를 git submodule로 추가하고, DataMonitor가 DataPersistence의 model/repository를 직접 재사용하도록 구조를 재편한다.

**Architecture:** 기존 DataMonitor 자체 `model/`, `repository/`를 제거하고 `DataPersistence/` 서브모듈에서 import한다. `config.py`가 sys.path를 설정하며 상태 상수(MONITORED_STATUSES, ACTIVE_STATUSES)를 str 리스트로 정의한다. [9] 메뉴에서 DummyDataGenerator를 subprocess로 호출해 더미 데이터를 생성한다.

**Tech Stack:** Python 3.x, git submodule, DataPersistence(SampleRepository/OrderRepository/Order/Sample), DummyDataGenerator CLI, pytest

---

## 파일 구조

```
DataMonitor/
├── .gitmodules                          ← 신규 (서브모듈 2개 등록)
├── DataPersistence/                     ← 서브모듈 (model, repository 제공)
├── DummyDataGenerator/                  ← 서브모듈 (CLI 더미 데이터 생성)
├── config.py                            ← 신규 (sys.path, DATA_DIR, 상태 상수)
├── conftest.py                          ← 신규 (pytest용 sys.path 초기화)
├── controller/
│   ├── __init__.py                      ← 신규
│   └── monitor_controller.py            ← 신규 (str 상태 기반 비즈니스 로직)
├── view/
│   ├── __init__.py                      ← 신규
│   └── monitor_view.py                  ← 신규 ([9] 메뉴 포함)
├── tests/
│   ├── __init__.py                      ← 신규
│   └── controller/
│       ├── __init__.py                  ← 신규
│       └── test_monitor_controller.py   ← 신규 (7개 테스트)
├── data/
│   ├── samples.json                     ← 신규 (시드 데이터)
│   └── orders.json                      ← 신규 (시드 데이터)
├── docs/
│   ├── PRD.md                           ← 수정 (구조 + [9] 메뉴 반영)
│   ├── PLAN.md                          ← 수정 (이 계획 파일로 교체)
│   └── superpowers/specs/...
├── CLAUDE.md                            ← 수정 (서브모듈 아키텍처 반영)
└── main.py                              ← 신규
```

---

## Task 1: 서브모듈 등록 및 문서 업데이트

**Files:**
- Create: `.gitmodules` (git submodule add 명령으로 자동 생성)
- Modify: `CLAUDE.md`
- Modify: `docs/PRD.md`
- Modify: `docs/PLAN.md`

- [ ] **Step 1: DataPersistence 서브모듈 추가**

```bash
git submodule add https://github.com/yeonho7/DataPersistence-yeonho-jeong-18013871.git DataPersistence
```

Expected: `DataPersistence/` 디렉터리 생성, `.gitmodules` 파일 생성

- [ ] **Step 2: DummyDataGenerator 서브모듈 추가**

```bash
git submodule add https://github.com/yeonho7/DummyDataGenerator-yeonho-jeong-18013871.git DummyDataGenerator
```

Expected: `DummyDataGenerator/` 디렉터리 생성

- [ ] **Step 3: 중첩 서브모듈 초기화 (DDG 내부의 DataPersistence)**

```bash
git submodule update --init --recursive
```

Expected: `DummyDataGenerator/DataPersistence/` 디렉터리 생성

- [ ] **Step 4: CLAUDE.md 업데이트**

`CLAUDE.md` 전체를 아래 내용으로 교체한다:

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

DataMonitor POC — 반도체 시료 생산주문관리 시스템의 데이터 상태를 콘솔에서 실시간 조회하는 관리자 도구.
전체 시스템 명세는 `docs/PRD.md`, 구현 계획은 `docs/PLAN.md` 참조.

## Submodules

| 경로 | 역할 |
|------|------|
| `DataPersistence/` | model(Sample, Order), repository(SampleRepository, OrderRepository) 제공 |
| `DummyDataGenerator/` | 더미 데이터 CLI 제공 ([9] 메뉴에서 subprocess로 호출) |

초기 설정:
```bash
git submodule update --init --recursive
```

## Architecture

MVC 패턴, 단방향 의존: `main.py` → `controller` → `DataPersistence/repository` → `DataPersistence/model`, `view` → (출력만)

```
DataPersistence/model/      도메인 모델 (Sample, Order) — 서브모듈 제공
DataPersistence/repository/ JSON 파일 CRUD (SampleRepository, OrderRepository) — 서브모듈 제공
controller/                 비즈니스 로직 (MonitorController — 주문 현황·재고 상태 계산)
view/                       콘솔 출력 전용 (MonitorView — 입출력, 비즈니스 로직 없음)
data/                       런타임 데이터 (samples.json, orders.json)
tests/                      controller 단위 테스트 (pytest) — model·repository는 DataPersistence에서 보장
config.py                   sys.path 설정 + DATA_DIR + 상태 상수
conftest.py                 pytest용 sys.path 초기화
```

`view/`는 테스트하지 않는다. 콘솔 I/O만 담당하며 로직이 없기 때문이다.
`model/`, `repository/`는 DataPersistence 서브모듈이 제공하므로 DataMonitor에 존재하지 않는다.

## Key Domain Rules

- Order.status는 str: "RESERVED" / "CONFIRMED" / "PRODUCING" / "RELEASED" / "REJECTED"
- MONITORED_STATUSES, ACTIVE_STATUSES는 `config.py`에 str 리스트로 정의됨
- 재고 상태: 고갈(stock=0) / 부족(stock < 활성주문합계) / 여유(그 외)
- 잔여율: `stock / (stock + 활성주문합계) * 100`, 활성주문 없으면 100.0
```

- [ ] **Step 5: docs/PRD.md 업데이트 — 프로젝트 구조 섹션**

`docs/PRD.md`의 섹션 5(프로젝트 구조)를 아래로 교체한다:

```markdown
## 5. 프로젝트 구조

```
DataMonitor/
├── DataPersistence/          # 서브모듈 — model, repository 제공
│   ├── model/
│   │   ├── sample.py         # Sample 도메인 모델
│   │   └── order.py          # Order 도메인 모델 (status: str)
│   └── repository/
│       ├── sample_repository.py
│       └── order_repository.py
├── DummyDataGenerator/       # 서브모듈 — 더미 데이터 CLI
├── config.py                 # sys.path 설정, DATA_DIR, 상태 상수
├── conftest.py               # pytest sys.path 초기화
├── controller/
│   └── monitor_controller.py # 모니터링 비즈니스 로직
├── view/
│   └── monitor_view.py       # 콘솔 출력 및 입력 ([9] 더미 데이터 생성 포함)
├── data/
│   ├── samples.json          # 시료 데이터
│   └── orders.json           # 주문 데이터
├── tests/
│   └── controller/
│       └── test_monitor_controller.py
└── main.py                   # 진입점
```
```

- [ ] **Step 6: docs/PRD.md 업데이트 — F-04 콘솔 UI 섹션**

`docs/PRD.md`의 F-04 항목에서 서브메뉴 목록을 아래로 수정한다:

```markdown
- 서브메뉴:
  - [1] 주문량 확인
  - [2] 재고량 확인
  - [9] 더미 데이터 생성 (DummyDataGenerator 호출)
  - [0] 종료
```

- [ ] **Step 7: docs/PLAN.md 교체**

`docs/PLAN.md` 전체를 아래로 교체한다:

```markdown
# DataMonitor POC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

상세 구현 계획: `docs/superpowers/plans/2026-05-08-submodule-integration.md` 참조.

## 요약

서브모듈 기반 아키텍처로 재편. DataPersistence 서브모듈의 model/repository를 직접 재사용하고,
DummyDataGenerator 서브모듈을 [9] 메뉴에서 subprocess로 호출한다.

## 핵심 변경 사항

- DataMonitor 자체 `model/`, `repository/` 없음 → DataPersistence 서브모듈 사용
- `Order.status`는 Enum 대신 str → 상태 상수를 `config.py`에서 str 리스트로 정의
- [9] 메뉴: DummyDataGenerator를 subprocess로 호출해 `data/` 생성
```

- [ ] **Step 8: Commit**

```bash
git add .gitmodules DataPersistence DummyDataGenerator CLAUDE.md docs/PRD.md docs/PLAN.md
git commit -m "chore: DataPersistence, DummyDataGenerator 서브모듈 등록 및 문서 업데이트"
```

---

## Task 2: 개발 환경 준비

**Files:**
- Create: `config.py`
- Create: `conftest.py`
- Create: `controller/__init__.py`
- Create: `view/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/controller/__init__.py`

- [ ] **Step 1: pytest 설치 확인**

```bash
.venv\Scripts\pip install pytest
```

Expected: `Successfully installed pytest-...` 또는 `Requirement already satisfied`

- [ ] **Step 2: config.py 생성**

`config.py`:
```python
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "DataPersistence"))

DATA_DIR = os.environ.get(
    "DATA_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"),
)
DATA_SAMPLES = os.path.join(DATA_DIR, "samples.json")
DATA_ORDERS = os.path.join(DATA_DIR, "orders.json")

MONITORED_STATUSES = ["RESERVED", "PRODUCING", "CONFIRMED", "RELEASED"]
ACTIVE_STATUSES = ["RESERVED", "PRODUCING", "CONFIRMED"]
```

- [ ] **Step 3: conftest.py 생성 (pytest용 sys.path 초기화)**

`conftest.py` (프로젝트 루트):
```python
import config  # noqa: F401  — DataPersistence/ 를 sys.path에 추가
```

- [ ] **Step 4: 패키지 __init__.py 생성**

아래 파일들을 빈 파일로 생성한다:
- `controller/__init__.py`
- `view/__init__.py`
- `tests/__init__.py`
- `tests/controller/__init__.py`

- [ ] **Step 5: DataPersistence import 가능 확인**

```bash
.venv\Scripts\python -c "import config; from model.sample import Sample; print(Sample.__dataclass_fields__)"
```

Expected: `{'sample_id': ..., 'name': ..., 'avg_production_time': ..., 'yield_rate': ..., 'stock': ...}`

- [ ] **Step 6: pytest 동작 확인**

```bash
.venv\Scripts\pytest tests/ -v
```

Expected: `no tests ran` (아직 테스트 없음)

- [ ] **Step 7: Commit**

```bash
git add config.py conftest.py controller/__init__.py view/__init__.py tests/
git commit -m "chore: config.py, conftest.py, 패키지 구조 초기화"
```

---

## Task 3: MonitorController (TDD)

**Files:**
- Create: `tests/controller/test_monitor_controller.py`
- Create: `controller/monitor_controller.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/controller/test_monitor_controller.py`:
```python
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
```

- [ ] **Step 4: 전체 테스트 통과 확인**

```bash
.venv\Scripts\pytest tests/controller/test_monitor_controller.py -v
```

Expected: `7 passed`

- [ ] **Step 5: Commit**

```bash
git add controller/monitor_controller.py tests/controller/test_monitor_controller.py
git commit -m "feat: MonitorController 비즈니스 로직 구현 (DataPersistence 서브모듈 활용)"
```

---

## Task 4: View, main.py, 시드 데이터

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
        print("  [9] 더미 데이터 생성")
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
    "status": "RESERVED",
    "created_at": "2026-05-08T00:00:00+00:00",
    "updated_at": "2026-05-08T00:00:00+00:00"
  },
  {
    "order_id": "ORD-20260508-0002",
    "sample_id": "S-003",
    "customer": "삼성전자 파운드리",
    "quantity": 200,
    "status": "PRODUCING",
    "created_at": "2026-05-08T00:00:00+00:00",
    "updated_at": "2026-05-08T00:00:00+00:00"
  },
  {
    "order_id": "ORD-20260508-0003",
    "sample_id": "S-001",
    "customer": "LG이노텍",
    "quantity": 300,
    "status": "CONFIRMED",
    "created_at": "2026-05-08T00:00:00+00:00",
    "updated_at": "2026-05-08T00:00:00+00:00"
  },
  {
    "order_id": "ORD-20260508-0004",
    "sample_id": "S-004",
    "customer": "DB하이텍",
    "quantity": 400,
    "status": "RELEASED",
    "created_at": "2026-05-08T00:00:00+00:00",
    "updated_at": "2026-05-08T00:00:00+00:00"
  },
  {
    "order_id": "ORD-20260508-0005",
    "sample_id": "S-002",
    "customer": "네패스",
    "quantity": 100,
    "status": "REJECTED",
    "created_at": "2026-05-08T00:00:00+00:00",
    "updated_at": "2026-05-08T00:00:00+00:00"
  }
]
```

- [ ] **Step 3: main.py 구현**

`main.py`:
```python
from __future__ import annotations
import os
import subprocess
import sys

import config
from config import DATA_SAMPLES, DATA_ORDERS, DATA_DIR
from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from controller.monitor_controller import MonitorController
from view.monitor_view import MonitorView


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
        elif choice == "9":
            subprocess.run(
                [sys.executable, "DummyDataGenerator/main.py"],
                env={**os.environ, "DATA_DIR": DATA_DIR},
            )
        elif choice == "0":
            view.display_message("종료합니다.")
            break
        else:
            view.display_message("올바른 메뉴를 선택하세요. (0/1/2/9)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 전체 테스트 통과 확인**

```bash
.venv\Scripts\pytest tests/ -v
```

Expected: `7 passed`

- [ ] **Step 5: 애플리케이션 수동 실행 확인**

```bash
.venv\Scripts\python main.py
```

확인 항목:
- 메인 메뉴에 `등록 시료 5종`, `총 재고 1,640 ea`, `전체 주문 4건` 표시
- [1] 선택 시 RESERVED 1건, PRODUCING 1건, CONFIRMED 1건, RELEASED 1건 (REJECTED 미포함)
- [2] 선택 시 SiC 파워기판-6인치 `[부족]`, 산화막 웨이퍼-SiO2 `[고갈]` 표시
- [9] 선택 시 DummyDataGenerator CLI 메뉴 진입 확인

- [ ] **Step 6: Commit**

```bash
git add view/ main.py data/
git commit -m "feat: MonitorView, main.py, 시드 데이터 추가"
```

---

## 검증 체크리스트

```bash
# 전체 테스트
.venv\Scripts\pytest tests/ -v

# 실행
.venv\Scripts\python main.py
```

- [ ] 서브모듈 `git submodule update --init --recursive` 정상 동작
- [ ] 7개 테스트 전체 통과
- [ ] 메인 화면에 시료 수 / 총 재고 / 주문 수 표시
- [ ] [1] 주문량 확인: RESERVED/PRODUCING/CONFIRMED/RELEASED 건수 및 목록, REJECTED 미포함
- [ ] [2] 재고량 확인: 시료별 재고 + 여유/부족/고갈 상태 + 잔여율
- [ ] [9] 더미 데이터 생성: DummyDataGenerator CLI 정상 진입
- [ ] Controller / View 패키지 명확히 분리 (model, repository는 DataPersistence 서브모듈)
