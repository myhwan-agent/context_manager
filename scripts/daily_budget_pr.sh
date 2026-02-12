#!/usr/bin/env bash
set -euo pipefail

REPO="myhwan-agent/context_manager"
DATE_LOCAL="${1:-$(date +%F)}"
BRANCH="pr/budget-${DATE_LOCAL}"

# Load local .env if present (do not commit secrets)
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

python3 scripts/budget_report.py "${DATE_LOCAL}" > "/tmp/budget_${DATE_LOCAL}.json"

DAY_USD=$(python3 -c 'import json; o=json.load(open("/tmp/budget_'"${DATE_LOCAL}"'.json")); print(o["day"]["total_usd"])')
MTD_USD=$(python3 -c 'import json; o=json.load(open("/tmp/budget_'"${DATE_LOCAL}"'.json")); print(o["mtd"]["total_usd"])')

mkdir -p budget/daily
cat > "budget/daily/${DATE_LOCAL}.md" <<EOF
# Budget — ${DATE_LOCAL}

## Source (billing)
- OpenAI Organization Costs API (Option A)

## 비용
- 당일 비용(USD): **$DAY_USD**
- 월 누적 비용(MTD, USD): **$MTD_USD**

## 메모
- 계산/집계 기준 시간대: Asia/Seoul
- raw json: /tmp/budget_${DATE_LOCAL}.json (local)
EOF

git fetch origin
git switch main
git pull --ff-only
git switch -C "${BRANCH}"

git add "budget/daily/${DATE_LOCAL}.md"
git commit -m "chore(budget): add billing cost for ${DATE_LOCAL}" || true
git push -u origin "${BRANCH}"

export PATH="/opt/homebrew/bin:$PATH"
if ! gh pr view --repo "$REPO" --head "$BRANCH" >/dev/null 2>&1; then
  gh pr create --repo "$REPO" --base main --head "$BRANCH" \
    --title "chore(budget): billing cost for ${DATE_LOCAL}" \
    --body "### 변경 사항\n- 당일 비용(USD): $DAY_USD\n- 월 누적(MTD, USD): $MTD_USD\n\n### Source\n- OpenAI Organization Costs API"
fi

echo "DONE: ${BRANCH}"
