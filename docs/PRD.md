# PRD: DataMonitor POC

## 1. 개요

### 배경
가상의 반도체 회사 S-Semi는 반도체 시료(Sample) 생산주문관리 시스템을 개발 중이다.
주문량 급증으로 엑셀·메모장 기반 관리의 한계가 드러났고,
재고·공정 현황을 한눈에 파악하기 어려운 문제가 발생했다.

본 시스템 개발에 앞서 4종의 PoC를 통해 핵심 기술을 검증한다.
DataMonitor는 그 중 하나로, **데이터 모니터링 패턴**을 검증한다.

### 목적
현재 저장된 데이터 상태를 콘솔에서 실시간 조회할 수 있는 관리자 도구를 구현한다.
본 PoC에서 검증한 패턴은 이후 `SampleOrderSystem` 본 프로젝트의 모니터링 기능에 적용된다.

### 범위
- PoC 항목: 데이터 모니터링 Tool
- Repository: `DataMonitor-본인영문이름-사번`
- 전체 PoC 목록: MVC 스켈레톤, 데이터 영속성 처리, **데이터 모니터링 Tool**, Dummy 데이터 생성 Tool

---

## 2. 도메인 모델

DataMonitor가 조회하는 데이터는 반도체 시료 생산주문관리 시스템의 핵심 도메인이다.

### 시료 (Sample)

| 필드 | 타입 | 설명 |
|------|------|------|
| sample_id | str | 고유 식별자 (예: S-001) |
| name | str | 시료명 (예: 실리콘 웨이퍼-8인치) |
| avg_production_time | float | 평균 생산시간 (min/ea) |
| yield_rate | float | 수율 — 정상 시료 / 총 생산 시료 (0.0 ~ 1.0) |
| stock | int | 현재 재고 수량 (ea) |

### 주문 (Order)

| 필드 | 타입 | 설명 |
|------|------|------|
| order_id | str | 주문번호 (형식: ORD-YYYYMMDD-XXXX) |
| sample_id | str | 시료 ID (FK) |
| customer | str | 고객명 |
| quantity | int | 주문 수량 (ea) |
| status | Enum | 아래 상태 참조 |

### 주문 상태 흐름

| 상태 | 의미 |
|------|------|
| RESERVED | 주문 접수 |
| REJECTED | 주문 거절 (모니터링 제외) |
| PRODUCING | 승인 완료, 재고 부족으로 생산 중 |
| CONFIRMED | 승인 완료, 출고 대기 중 |
| RELEASED | 출고 완료 |

상태 전이:
```
RESERVED → (승인, 재고 충분) → CONFIRMED → (출고) → RELEASED
RESERVED → (승인, 재고 부족) → PRODUCING → (생산 완료) → CONFIRMED → (출고) → RELEASED
RESERVED → (거절) → REJECTED
```

---

## 3. 기능 요구사항

### F-01: 주문 현황 조회
- 상태별(RESERVED / PRODUCING / CONFIRMED / RELEASED) 주문 건수 표시
- REJECTED는 표시에서 제외
- 각 상태별 주문 목록(주문번호, 고객명, 시료명, 수량) 확인 가능

### F-02: 시료 재고 현황 조회
- 등록된 모든 시료의 현재 재고 수량 표시
- 주문 대비 재고 상태 표기:
  - **여유**: 현재 재고 ≥ 활성 주문 수량 합계
  - **부족**: 0 < 현재 재고 < 활성 주문 수량 합계
  - **고갈**: 현재 재고 = 0
- 잔여율(%) 표시: `재고 / (재고 + 활성 주문 합계) * 100`

### F-03: 데이터 영속성
- JSON 파일 기반으로 데이터 저장 및 로드
- `data/samples.json`, `data/orders.json` 파일 사용
- 애플리케이션 재시작 후에도 데이터 유지 (CRUD 포함)

### F-04: 콘솔 UI
- 메인 화면: 시스템 현황 요약 (등록 시료 수, 총 재고, 전체 주문 수)
- 서브메뉴:
  - [1] 주문량 확인
  - [2] 재고량 확인
  - [9] 더미 데이터 생성 (DummyDataGenerator 호출)
  - [0] 종료

---

## 4. 비기능 요구사항

- **플랫폼**: Python 3.x 콘솔 애플리케이션
- **아키텍처**: MVC 패턴 (Model / View / Controller 패키지 분리)
- **저장소**: JSON 파일 (`data/` 디렉터리)
- **외부 의존성**: 표준 라이브러리만 사용 (PoC 검증 목적)
- **가독성**: 상태에 따른 텍스트 레이블 구분 표기

---

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

---

## 6. 기술 스택

| 항목 | 선택 | 이유 |
|------|------|------|
| 언어 | Python 3.x | 기존 .venv 존재, 빠른 프로토타이핑 |
| 데이터 저장 | JSON 파일 | 별도 DB 설치 불필요, 사람이 읽을 수 있음 |
| 아키텍처 | MVC | 과제 요건 (Model/Controller/View 패키지 분리) |
| 외부 라이브러리 | 없음 | PoC이므로 의존성 최소화 |

---

## 7. 성공 기준

- [ ] 콘솔 메뉴에서 주문 상태별 현황(RESERVED/PRODUCING/CONFIRMED/RELEASED 건수) 조회 가능
- [ ] 콘솔 메뉴에서 시료별 재고 수량 및 상태(여유/부족/고갈) 조회 가능
- [ ] `data/samples.json`, `data/orders.json` 파일에서 데이터 로드 가능
- [ ] 애플리케이션 재시작 후에도 데이터 유지
- [ ] Model / View / Controller 패키지가 명확히 분리됨

---

## 8. 검증 방법

1. `python main.py` 실행 → 메인 화면(시료 수, 총 재고, 주문 수) 및 메뉴 표시 확인
2. [1] 주문량 확인 → 상태별 건수 및 목록 출력 확인, REJECTED 미포함 확인
3. [2] 재고량 확인 → 시료별 재고 수량 + 여유/부족/고갈 상태 및 잔여율 출력 확인
4. `data/*.json` 수동 편집 후 재실행 → 변경된 데이터 반영 확인
