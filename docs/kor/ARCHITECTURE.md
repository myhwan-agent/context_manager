# 아키텍처 (초안)

기반 프레임워크는 **LangGraph**로 구성한다.

## 개념

### Event
무슨 일이 일어났는지 기록하는 append-only 레코드
- observation / action / plan / tool / note

### View (제한된 컨텍스트 출력)
소비자별로 필요한 컨텍스트 뷰가 다르다.
- Planner context (압축/태스크 중심)
- Debug context (상세 로그 중심)
- Retrieval context (memory hit 중심)

### Namespace (옵션 분리)
이벤트는 태그를 가질 수 있다.
- perception
- planning
- tools
- human

분리 방식:
- namespace별 summary 스트림 분리
- 또는 뷰별 include/exclude 선택

## 제안 LangGraph 파이프라인 (M1)

State:
- events (bounded list)
- summaries (namespace별 + global)
- memory_store handle (pluggable)

초기 노드:
1) ingest_event
2) window_history (최근 N개 유지)
3) summarize (현재는 stub)
4) build_planning_context

출력:
- planning_context: str

## 확정이 필요한 질문
1) 언어/런타임: Python only로 갈지?
2) persistence를 지금 넣을지(sqlite/jsonl), 아니면 후순위로 둘지?
3) 1 FPS 기준으로 매 프레임 요약할지, 트리거 기반으로 요약할지?
