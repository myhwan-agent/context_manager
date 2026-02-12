#!/usr/bin/env bash
set -euo pipefail

DATE_LOCAL="${1:-$(date +%F)}"

# Load local secret env
if [ -f /Users/ai-agent/Desktop/myhwan-agent.sh ]; then
  # shellcheck disable=SC1091
  source /Users/ai-agent/Desktop/myhwan-agent.sh
fi
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
- 집계 기준 시간대: Asia/Seoul
- raw json: /tmp/budget_${DATE_LOCAL}.json (local)
EOF

git switch main
git pull --ff-only

git add "budget/daily/${DATE_LOCAL}.md"
if ! git diff --cached --quiet; then
  git commit -m "chore(budget): update billing cost for ${DATE_LOCAL}"
  git push origin main
  echo "UPDATED: budget/daily/${DATE_LOCAL}.md pushed to main"
else
  echo "NO_CHANGE: budget/daily/${DATE_LOCAL}.md already up-to-date"
fi
