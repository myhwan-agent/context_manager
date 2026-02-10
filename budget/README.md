# budget/

모델 사용량/비용을 일 단위로 기록.

## 목표
- **매일 비용(당일)** + **누적 비용(MTD)** 를 함께 기록
- 가능하면 **추정이 아니라 billing/usage API** 기반으로 기록

## Sources
- OpenAI Platform pricing (단가 표): https://platform.openai.com/pricing
- (권장) OpenAI billing/usage API: OPENAI_API_KEY 기반

## Files
- `budget/pricing_sources.md` : 단가 레퍼런스/가정
- `budget/daily/YYYY-MM-DD.md` : 일별 기록

## Automation
- `scripts/budget_report.py YYYY-MM-DD` : billing API로 당일/MTD 비용을 JSON으로 출력
- `scripts/daily_budget_pr.sh [YYYY-MM-DD]` : budget 파일 업데이트 → 브랜치 → PR 생성

## Required env vars (Option A)
- `OPENAI_API_KEY` (required)
- `OPENAI_API_BASE` (optional, default: https://api.openai.com)
- `OPENAI_ORG_ID` (optional)
- `OPENAI_PROJECT_ID` (optional)

Note: 키는 레포에 커밋하지 말고, 로컬 환경변수/시크릿으로 주입.
