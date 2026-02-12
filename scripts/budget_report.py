#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com").rstrip("/")
API_KEY = os.getenv("OPENAI_API_KEY", "")
ORG_ID = os.getenv("OPENAI_ORG_ID", "")
PROJECT_ID = os.getenv("OPENAI_PROJECT_ID", "")


def _utc_day_range(day_local: dt.date, tz: dt.tzinfo) -> tuple[int, int]:
    start_local = dt.datetime.combine(day_local, dt.time.min).replace(tzinfo=tz)
    end_local = dt.datetime.combine(day_local, dt.time.max).replace(tzinfo=tz)
    return int(start_local.astimezone(dt.timezone.utc).timestamp()), int(
        end_local.astimezone(dt.timezone.utc).timestamp()
    )


def _utc_month_to_date_range(day_local: dt.date, tz: dt.tzinfo) -> tuple[int, int]:
    first = day_local.replace(day=1)
    return _utc_day_range(first, tz)[0], _utc_day_range(day_local, tz)[1]


@dataclass
class CostResult:
    total_usd: float
    raw: dict[str, Any]


def _request_json(url: str) -> dict[str, Any]:
    if not API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {API_KEY}")
    if ORG_ID:
        req.add_header("OpenAI-Organization", ORG_ID)
    if PROJECT_ID:
        req.add_header("OpenAI-Project", PROJECT_ID)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_costs(start_time: int, end_time: int) -> CostResult:
    qs = urllib.parse.urlencode({"start_time": start_time, "end_time": end_time})
    obj = _request_json(f"{API_BASE}/v1/organization/costs?{qs}")
    total = 0.0
    if isinstance(obj.get("total_cost"), (int, float)):
        total = float(obj["total_cost"])
    else:
        for row in obj.get("data") or []:
            amount = (row.get("amount") or {}).get("value")
            if isinstance(amount, (int, float)):
                total += float(amount)
    return CostResult(total, obj)


def main() -> int:
    import sys

    tz = dt.timezone(dt.timedelta(hours=9))  # Asia/Seoul
    day = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.datetime.now(tz).date()

    day_start, day_end = _utc_day_range(day, tz)
    mtd_start, mtd_end = _utc_month_to_date_range(day, tz)

    day_cost = fetch_costs(day_start, day_end)
    mtd_cost = fetch_costs(mtd_start, mtd_end)

    print(
        json.dumps(
            {
                "date": day.isoformat(),
                "day": {
                    "start_time": day_start,
                    "end_time": day_end,
                    "total_usd": day_cost.total_usd,
                },
                "mtd": {
                    "start_time": mtd_start,
                    "end_time": mtd_end,
                    "total_usd": mtd_cost.total_usd,
                },
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
