# Context History Strategy (Plan–Act 루프)

목표: 장기 Plan→Act→Verify→(Replan) 루프에서도 컨텍스트를 작고, 관련성 높고, 견고하게 유지한다.

## 문제 정의
- 초기 long-horizon plan 생성: ~10초
- 스텝별 verify: ~1초 (최신 observation + executor result)
- history는 빠르게 증가(프레임 + tool 로그 + 에러)

## 실전 패턴 (2023–2025)

### 1) Event sourcing + **이중 메모리**(working set + long-term)
- 작은 working context(최근 윈도우 + rolling summary) 유지
- 전체 이벤트 로그는 별도 저장소(DB)에 보존 후 선택 조회
- 가상 메모리/계층 메모리 아이디어와 정합

참고:
- MemGPT: https://arxiv.org/abs/2310.08560

### 2) 경계(boundary) 트리거 기반 요약 (프레임마다 X)
다음 시점에서만 요약:
- action boundary (executor 결과 직후)
- plan boundary (subtask 완료/phase 변경)
- failure boundary (verify fail/에러)

이 방식이 1 FPS를 맞추는 가장 현실적인 방법.

### 3) 계층형 요약 (episode → session)
- Episode summary: subtask/액션 chunk 단위
- Session summary: episode 롤업
- object 위치/제약/목표 같은 핵심 facts는 key-value로 유지

참고:
- Generative Agents: https://arxiv.org/abs/2304.03442

### 4) Plan–Act 인터리빙(ReAct 스타일)
짧고 구조화된 트레이스로 유지:
- PLAN: 시도 의도
- ACT: 실행 내용
- OBS/RESULT: 관측/결과
- NEXT: 다음 액션

참고:
- ReAct: https://arxiv.org/abs/2210.03629

### 5) 실패 주도 reflection (replanning 트리거)
실패 시 짧은 reflection 기록(실패 원인/다음 시도)을 남기고 replan.

참고:
- Reflexion: https://arxiv.org/abs/2303.11366

## 본 레포 제안 스펙 (1차)

### State 표현
- `recent_events`: 최근 N개 이벤트 (bounded)
- `rolling_summary`: 과거 이벤트 압축 텍스트
- `facts`: 구조화 핵심 사실(object→global pose 등)
- `current_plan`: 현재 long-horizon plan (chunk 가능)
- `step_index`: 현재 스텝

### 압축 정책 (가볍고 효과적)
- 전체 이벤트는 event log(DB)에 누적 저장
- working state에서는:
  - 최근 N개는 원문 유지
  - 예산 초과 시 오래된 K개를 `rolling_summary`로 fold
  - `facts`는 별도 유지(압축으로 핵심 상태 손실 방지)

### Verify 컨텍스트
Verifier에는 최소 정보만 제공:
- 직전 action
- executor result
- 최신 observation(인코딩 텍스트)
- 현재 subtask + 제약
- 최소 facts

이 구성으로 verify를 1초 이내로 유지한다.
