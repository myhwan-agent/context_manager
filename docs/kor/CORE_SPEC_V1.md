# Context Manager Core Spec v1

상태: Draft (2026-02-18)

## 1) Executor Result 포맷 (초안)

결정사항:
- executor 결과는 JSON으로 전달
- 최소 필수: success/fail + error_code + 실패 이유 텍스트

```json
{
  "action_id": "a-20260218-0001",
  "plan_id": "p-20260218-01",
  "step_index": 3,
  "action": {
    "name": "pick",
    "args": {"object": "mug"}
  },
  "status": "success",
  "error_code": null,
  "error_reason": null,
  "latency_ms": 740,
  "ts": "2026-02-18T18:55:01+09:00",
  "meta": {}
}
```

실패 예시:
```json
{
  "action_id": "a-20260218-0002",
  "plan_id": "p-20260218-01",
  "step_index": 4,
  "action": {
    "name": "place",
    "args": {"object": "mug", "target": "coaster"}
  },
  "status": "fail",
  "error_code": "NO_GRASP",
  "error_reason": "gripper lost contact while moving",
  "latency_ms": 920,
  "ts": "2026-02-18T18:55:02+09:00",
  "meta": {"retryable": true}
}
```

## 2) Replanning Trigger
- 현재 Open Question으로 유지
- TODO: 정책 확정 전까지 `docs/kor/OPEN_QUESTIONS.md`에 후보 규칙 기록

## 3) Token Budget 권장안 (qwen3-vl-32b, 1 FPS 목표)

원칙:
- Verify 루프(1초 이내)는 작고 고정된 컨텍스트
- Planner는 더 길게 가져가되, 트리거 기반 요약으로만 갱신

권장 시작값:
- **Verify Context:** 2k~3k tokens
  - 직전 action + executor_result + 최신 observation + 핵심 facts
- **Planner Context:** 8k~12k tokens
  - rolling summary + recent events + current goal/constraints
- **Hard Cutoff:** 16k tokens
  - 16k 초과 시 강제 압축(fold) + low-priority 이벤트 드랍

이유:
- 1 FPS 루프에서 매 스텝 긴 프롬프트는 지연/비용을 급격히 증가시킴
- Verify는 판정 중심이라 정보량이 적어도 됨
- 장기 계획은 summary 기반으로 안정적으로 유지 가능

## 4) Core Runtime View

- `recent_events` (최근 N개 원본)
- `rolling_summary` (과거 압축)
- `facts` (object 위치/상태 등 structured)
- `current_plan` + `step_index`
- `failure_memory` (반복 실패 패턴)

## 5) 구현 순서 (v1)
1. executor_result 파서 + validation
2. verify context builder (2k~3k 예산)
3. planner context builder (8k~12k 예산)
4. budget guard (16k hard cutoff)
5. replanning trigger는 open question 상태로 hook만 구현
