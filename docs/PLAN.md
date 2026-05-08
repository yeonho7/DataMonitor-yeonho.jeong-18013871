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
