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
