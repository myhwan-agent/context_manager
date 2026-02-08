# budget/

모델 사용량/비용을 일 단위로 기록.

원칙:
- OpenClaw `session_status` 기준으로 토큰 사용량을 기록
- 비용은 **공개된 단가(레퍼런스 링크 포함)** 기반으로 추정치를 기록
- 모델명이 공개 단가 테이블과 1:1로 매칭되지 않으면, 가정(assumption)을 명시하고 추후 소급 재계산

파일:
- `budget/pricing_sources.md` (단가 레퍼런스/가정)
- `budget/daily/YYYY-MM-DD.md`
