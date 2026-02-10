#!/usr/bin/env bash
set -euo pipefail

# Creates a PR that updates budget/daily/YYYY-MM-DD.md with:
# - that day's cost
# - month-to-date cumulative cost

REPO="myhwan-agent/context_manager"
DATE_LOCAL="${1:-$(date +%F)}"
BRANCH="pr/budget-${DATE_LOCAL}"

# requirements: gh authenticated, OPENAI_API_KEY set

python3 scripts/budget_report.py "${DATE_LOCAL}" > "/tmp/budget_${DATE_LOCAL}.json"

DAY_USD=$(python3 -c 'import json; o=json.load(open("/tmp/budget_'"${DATE_LOCAL}"'.json")); print(o["day"]["total_usd"])')
MTD_USD=$(python3 -c 'import json; o=json.load(open("/tmp/budget_'"${DATE_LOCAL}"'.json")); print(o["mtd"]["total_usd"])')

mkdir -p budget/daily
cat > "budget/daily/${DATE_LOCAL}.md" <<EOF
# Budget — ${DATE_LOCAL}

## Source (billing)
- OpenAI Organization Costs API (via OPENAI_API_KEY)

## 비용
- 당일 비용(USD): **$DAY_USD**
- 월 누적 비용(MTD, USD): **$MTD_USD**

## Raw
- JSON: see /tmp/budget_${DATE_LOCAL}.json (local)
EOF

# git workflow

git fetch origin

git switch main

git pull --ff-only

git switch -C "${BRANCH}"

git add "budget/daily/${DATE_LOCAL}.md"

git commit -m "chore(budget): add billing cost for ${DATE_LOCAL}" || true

git push -u origin "${BRANCH}"

export PATH="/opt/homebrew/bin:$PATH"

# Create PR if not exists
if ! gh pr view --repo "$REPO" --head "$BRANCH" >/dev/null 2>&1; then
  gh pr create --repo "$REPO" --base main --head "$BRANCH" \
    --title "chore(budget): billing cost for ${DATE_LOCAL}" \
    --body "- 당일 비용(USD): $DAY_USD\n- 월 누적(MTD, USD): $MTD_USD\n\nSource: OpenAI Organization Costs API"
fi

echo "DONE: ${BRANCH}"
