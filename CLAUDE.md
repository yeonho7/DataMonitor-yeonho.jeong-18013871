# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

DataMonitor POC — 반도체 시료 생산주문관리 시스템의 데이터 상태를 콘솔에서 실시간 조회하는 관리자 도구.
전체 시스템 명세는 `docs/PRD.md`, 구현 계획은 `docs/PLAN.md` 참조.

## Commands

```bash
# 애플리케이션 실행
.venv\Scripts\python main.py

# 전체 테스트
.venv\Scripts\pytest tests/ -v

# 특정 테스트 파일
.venv\Scripts\pytest tests/controller/test_monitor_controller.py -v

# 특정 테스트 함수
.venv\Scripts\pytest tests/controller/test_monitor_controller.py::test_stock_status_short -v

# pytest 설치 (최초 1회)
.venv\Scripts\pip install pytest
```

## Architecture

MVC 패턴, 단방향 의존: `main.py` → `controller` → `repository` → `model`, `view` → (출력만)

```
model/          도메인 모델 (Sample, Order, OrderStatus Enum)
repository/     JSON 파일 CRUD (SampleRepository, OrderRepository)
controller/     비즈니스 로직 (MonitorController — 주문 현황·재고 상태 계산)
view/           콘솔 출력 전용 (MonitorView — 입출력, 비즈니스 로직 없음)
data/           런타임 데이터 (samples.json, orders.json)
tests/          model·repository·controller 단위 테스트 (pytest)
```

`view/`는 테스트하지 않는다. 콘솔 I/O만 담당하며 로직이 없기 때문이다.

## Key Domain Rules

- `OrderStatus`: RESERVED → CONFIRMED(재고 충분) 또는 PRODUCING(재고 부족) → CONFIRMED → RELEASED
- REJECTED는 모니터링에서 제외. `MONITORED_STATUSES`와 `ACTIVE_STATUSES`는 `model/order.py`에 상수로 정의됨
- 재고 상태: 고갈(stock=0) / 부족(stock < 활성주문합계) / 여유(그 외)
- 잔여율: `stock / (stock + 활성주문합계) * 100`, 활성주문 없으면 100.0
- 실 생산량 계산 (본 PoC 범위 밖, SampleOrderSystem에서 사용): `ceil(부족분 / (수율 * 0.9))`

## Data Persistence

Repository 클래스가 초기화 시 JSON 파일을 로드하고, `save()` 호출 시마다 즉시 파일에 기록한다.
파일이 없으면 빈 상태로 시작한다 (예외 없음). 경로는 `main.py`에서 문자열로 주입한다.

## Test Fixtures

Repository 테스트는 `pytest`의 `tmp_path` 픽스처로 임시 JSON 파일을 사용한다.
실제 `data/` 파일을 건드리지 않는다.
