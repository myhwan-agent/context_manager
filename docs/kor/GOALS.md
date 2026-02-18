# Context Manager — 목표 (초안)

대상 사용 사례: 로봇 액션을 구동하는 Vision-Language Model(VLM)
- 모델: qwen3-vl-32b
- 런타임 목표: 약 1 FPS 루프
- 문제: 컨텍스트 윈도우가 빠르게 커지며, 길어질수록 이해도 저하 + 비용 증가

## 핵심 책임

1) **컨텍스트 요약/압축**
- 계획에 적합한 컴팩트 상태 표현 생성
- 태스크 관련 정보는 보존하고 노이즈는 제거

2) **컨텍스트 기록/메모리**
- 관측, 의사결정, 액션, 결과 저장
- 관련성/최신성 기반 조회 지원

3) **컨텍스트 히스토리**
- 최근 타임라인과 주요 전환점 제공
- 제한된 범위의 “N step back” 재구성 지원

4) **컨텍스트 분리(isolate, optional)**
- planning / perception / tool 출력 관심사 분리
- tool chatter로 인한 오염/과적합 방지

## 비목표(현재)
- 풀 에이전트 프레임워크 구현
- 필요 이상으로 무거운 외부 의존성 도입

## 1차 마일스톤
- M1: 이벤트를 입력받아 planning context를 출력하는 최소 LangGraph 파이프라인
- M2: 교체 가능한 summarizer + memory store 인터페이스 추가
- M3: history windowing + isolation namespace 추가
