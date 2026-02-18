# Open Questions

## Replanning Trigger Policy

아직 확정 전. 후보안:

1) Immediate Replan
- fail 1회 발생 시 즉시 replanning

2) Error-class Aware
- 치명적 에러(`UNREACHABLE`, `COLLISION_RISK`)는 즉시 replan
- 일시적 에러(`NO_GRASP`, `SLIP`)는 N회 재시도 후 replan

3) Budget-aware
- 연속 실패 + token budget pressure가 높을 때는 빠르게 replan

결정 필요 파라미터:
- retry 횟수
- fatal error_code 목록
- backoff 규칙
