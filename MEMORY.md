# MEMORY.md (Long-term Project Memory)

이 파일은 프로젝트의 장기 기억(핵심 결정/원칙/중요 맥락)을 기록한다.

## Project Identity
- Project: context_manager
- Goal: Long-horizon Plan-Act-Verify 루프에서 context를 안정적으로 관리
- Target: qwen3-vl-32b, ~1 FPS

## Fixed Decisions
- Context manager 핵심 기능: 요약/압축, 기록/메모리, 히스토리, isolate(optional)
- Billing은 Option A(실제 API 기반) 우선
- budget 업데이트는 daily 파일로 운영

## Current Core Spec Snapshot
- executor_result: JSON(success/fail + error_code + error_reason)
- replanning trigger: open question
- token budget start point:
  - verify: 2k~3k
  - planner: 8k~12k
  - hard cutoff: 16k

## Change Log Rules
- 큰 결정 변경 시: 날짜 + 이유 + 영향 범위 기록
- 세부 로그는 `memory/YYYY-MM-DD.md`에 기록 후 중요한 것만 여기로 승격
