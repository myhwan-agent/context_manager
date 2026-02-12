# budget/

모델 사용량/비용을 일 단위로 기록.

## 목표
- **매일 비용(당일)** + **월 누적 비용(MTD)** 를 함께 기록
- 추정치가 아닌 billing API(Option A) 기준으로 기록

## 파일
- `budget/daily/YYYY-MM-DD.md` : 일별 비용 기록
- `budget/pricing_sources.md` : 참고 단가/레퍼런스

## 자동화 스크립트
- `scripts/budget_report.py [YYYY-MM-DD]`
  - OpenAI Organization Costs API를 호출해 day/mtd 비용(JSON) 출력
- `scripts/daily_budget_pr.sh [YYYY-MM-DD]`
  - budget 파일 생성 → 브랜치 푸시 → PR 자동 생성

## 환경변수(Option A)
- `OPENAI_API_KEY` (필수)
- `OPENAI_API_BASE` (선택, 기본 `https://api.openai.com`)
- `OPENAI_ORG_ID` (선택)
- `OPENAI_PROJECT_ID` (선택)

실제 키는 `.env` 또는 로컬 환경변수로만 관리하고, 레포에는 커밋하지 않는다.
