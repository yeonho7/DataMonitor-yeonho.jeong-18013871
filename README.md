# DataMonitor

반도체 시료 생산주문관리 시스템의 데이터 상태를 콘솔에서 실시간 조회하는 관리자 도구 (PoC).

> **PoC 목적:** 데이터 모니터링 패턴을 검증한다. 검증된 패턴은 이후 `SampleOrderSystem` 본 프로젝트에 적용된다.

---

## 사전 조건

- Python 3.10 이상

---

## 실행

```bash
python main.py
```

메인 화면에서 등록 시료 수·총 재고·전체 주문 건수를 확인하고 메뉴를 선택한다.

| 메뉴 | 기능 |
|------|------|
| `1` | 주문 현황 (상태별 건수 및 목록) |
| `2` | 재고 현황 (시료별 재고·상태·잔여율) |
| `9` | 더미 데이터 생성 (DummyDataGenerator 호출) |
| `0` | 종료 |

---

## 테스트

```bash
pytest
```

`tests/controller/` 아래 `MonitorController` 단위 테스트가 실행된다.  
`view/`는 콘솔 I/O만 담당하므로 테스트하지 않는다.

---

## 프로젝트 구조

```
DataMonitor/
├── DataPersistence/          # 서브모듈 — Sample·Order 모델 및 JSON Repository 제공
├── DummyDataGenerator/       # 서브모듈 — 더미 데이터 CLI ([9] 메뉴에서 호출)
├── controller/
│   └── monitor_controller.py # 주문 현황·재고 상태 계산 (비즈니스 로직)
├── view/
│   └── monitor_view.py       # 콘솔 출력 전용 (로직 없음)
├── data/
│   ├── samples.json          # 시료 데이터 (런타임 자동 생성)
│   └── orders.json           # 주문 데이터 (런타임 자동 생성)
├── tests/
│   └── controller/
│       └── test_monitor_controller.py
├── config.py                 # sys.path 설정, DATA_DIR, 상태 상수
├── conftest.py               # pytest sys.path 초기화
└── main.py                   # 진입점
```

의존 방향: `main.py` → `controller` → `DataPersistence/repository` → `DataPersistence/model`

---

## 데이터 파일

`data/samples.json`, `data/orders.json` 파일에 JSON 형식으로 저장된다.  
파일이 없으면 첫 실행 시 자동으로 생성된다. 수동 편집 후 재실행하면 변경 내용이 즉시 반영된다.
