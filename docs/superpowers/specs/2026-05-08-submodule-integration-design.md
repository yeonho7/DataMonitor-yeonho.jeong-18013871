# DataMonitor 서브모듈 통합 설계

**날짜:** 2026-05-08  
**범위:** DataPersistence, DummyDataGenerator 서브모듈 통합 및 DataMonitor 구조 재편

---

## 배경

DataMonitor는 4종 PoC 중 하나로, 나머지 두 PoC인 DataPersistence(데이터 영속성)와 DummyDataGenerator(더미 데이터 생성)를 git submodule로 활용한다. 코드 중복을 없애고 단일 도메인 모델을 유지하는 것이 목적이다.

---

## 서브모듈 구성

| 서브모듈 경로 | URL | 용도 |
|---|---|---|
| `DataPersistence/` | https://github.com/yeonho7/DataPersistence-yeonho-jeong-18013871.git | model, repository 제공 |
| `DummyDataGenerator/` | https://github.com/yeonho7/DummyDataGenerator-yeonho-jeong-18013871.git | 더미 데이터 CLI 제공 |

DummyDataGenerator는 자체적으로 DataPersistence 서브모듈을 포함하므로, DataMonitor의 서브모듈 트리는 다음과 같다:

```
DataMonitor/
├── DataPersistence/          ← DataMonitor 직접 참조
└── DummyDataGenerator/
    └── DataPersistence/      ← DDG가 참조 (별도 복사본)
```

---

## 아키텍처

### 디렉터리 구조

```
DataMonitor/
├── .gitmodules
├── DataPersistence/              ← 서브모듈
├── DummyDataGenerator/           ← 서브모듈
├── config.py                     ← sys.path 설정, DATA_DIR, 상태 상수
├── controller/
│   ├── __init__.py
│   └── monitor_controller.py     ← DataPersistence 타입 직접 사용
├── view/
│   ├── __init__.py
│   └── monitor_view.py           ← [9] 더미 데이터 생성 메뉴 포함
├── tests/
│   ├── __init__.py
│   └── controller/
│       ├── __init__.py
│       └── test_monitor_controller.py
├── data/
│   ├── samples.json
│   └── orders.json
├── docs/
│   ├── PRD.md
│   └── PLAN.md
└── main.py
```

**제거:** DataMonitor 자체 `model/`, `repository/` 디렉터리 (DataPersistence 서브모듈로 대체).

### 의존성 방향

```
main.py → controller → DataPersistence/repository → DataPersistence/model
main.py → view → (출력만)
main.py → DummyDataGenerator/main.py (subprocess, [9] 선택 시)
config.py → (sys.path 설정, 모든 레이어에서 import)
```

---

## 상세 설계

### config.py

```python
import os, sys

# DataPersistence 모듈을 import 가능하게 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "DataPersistence"))

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))
DATA_SAMPLES = os.path.join(DATA_DIR, "samples.json")
DATA_ORDERS  = os.path.join(DATA_DIR, "orders.json")

# DataPersistence의 Order.status는 str이므로 상수를 여기서 정의
MONITORED_STATUSES = ["RESERVED", "PRODUCING", "CONFIRMED", "RELEASED"]
ACTIVE_STATUSES    = ["RESERVED", "PRODUCING", "CONFIRMED"]
```

### MonitorController

`from model.sample import Sample`, `from model.order import Order`, `from repository.sample_repository import SampleRepository`, `from repository.order_repository import OrderRepository`로 DataPersistence 레이어를 직접 사용.

`MONITORED_STATUSES`, `ACTIVE_STATUSES`는 config에서 가져온 str 리스트로 상태 필터링.

### View — 메뉴 구성

```
[1] 주문량 확인
[2] 재고량 확인
[9] 더미 데이터 생성
[0] 종료
```

[9] 선택 시 `subprocess.run(["python", "DummyDataGenerator/main.py"], env={**os.environ, "DATA_DIR": DATA_DIR})` 호출. DataMonitor의 `data/` 디렉터리를 DDG의 출력 경로로 지정.

### 테스트 범위

DataPersistence의 model, repository는 DataPersistence 자체 테스트로 보장됨. DataMonitor 테스트는 `controller/` 로직만 커버.

| 테스트 파일 | 검증 대상 |
|---|---|
| `tests/controller/test_monitor_controller.py` | get_summary, get_order_status_summary, get_stock_status, 잔여율 계산 |

테스트에서 DataPersistence Repository를 직접 사용하며 `tmp_path` fixture로 임시 JSON 파일 격리.

---

## 호환성 노트

| 항목 | DataMonitor 기존 PLAN | 변경 후 |
|---|---|---|
| Order.status 타입 | `OrderStatus` Enum | `str` (DataPersistence 그대로) |
| 상태 상수 위치 | `model/order.py` | `config.py` (str 리스트) |
| model/ 위치 | DataMonitor 자체 | `DataPersistence/model/` |
| repository/ 위치 | DataMonitor 자체 | `DataPersistence/repository/` |
| 시드 데이터 방식 | 수동 JSON 파일 | [9] 메뉴로 DDG 호출 |

---

## 성공 기준

- [ ] `.gitmodules`에 두 서브모듈 등록, `git submodule update --init --recursive` 시 정상 초기화
- [ ] `config.py`의 sys.path 설정으로 DataPersistence model/repository import 가능
- [ ] 기존 F-01, F-02 기능(주문 현황, 재고 현황) 정상 동작
- [ ] [9] 메뉴 선택 시 DDG가 `data/` 디렉터리에 샘플/주문 데이터 생성
- [ ] controller 테스트 전체 통과
