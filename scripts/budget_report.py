#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Optional


API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com").rstrip("/")
API_KEY = os.getenv("OPENAI_API_KEY", "")
ORG_ID = os.getenv("OPENAI_ORG_ID", "")  # optional
PROJECT_ID = os.getenv("OPENAI_PROJECT_ID", "")  # optional


def _utc_day_range(day_local: dt.date, tz: dt.tzinfo) -> tuple[int, int]:
    """Return (start_time,end_time) in unix seconds for a local day."""

    start_local = dt.datetime.combine(day_local, dt.time.min).replace(tzinfo=tz)
    end_local = dt.datetime.combine(day_local, dt.time.max).replace(tzinfo=tz)
    start_utc = start_local.astimezone(dt.timezone.utc)
    end_utc = end_local.astimezone(dt.timezone.utc)
    return int(start_utc.timestamp()), int(end_utc.timestamp())


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
    # Project scoping differs by account; we include it if set.
    if PROJECT_ID:
        req.add_header("OpenAI-Project", PROJECT_ID)

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read().decode("utf-8")
    return json.loads(data)


def fetch_costs(start_time: int, end_time: int) -> CostResult:
    """Fetch costs via OpenAI Organization Costs endpoint.

    Endpoint is subject to change; if it fails, we surface raw error upstream.

    Reference (pricing/usage docs entry point):
    - https://platform.openai.com/pricing
    """

    qs = urllib.parse.urlencode({"start_time": start_time, "end_time": end_time})
    url = f"{API_BASE}/v1/organization/costs?{qs}"
    obj = _request_json(url)

    # Best-effort extraction: some responses include a top-level 'total_cost' or sum of data[].amount.value
    total = 0.0
    if isinstance(obj.get("total_cost"), (int, float)):
        total = float(obj["total_cost"])
    else:
        data = obj.get("data") or []
        for row in data:
            amount = (row.get("amount") or {}).get("value")
            if isinstance(amount, (int, float)):
                total += float(amount)

    return CostResult(total_usd=total, raw=obj)


def main() -> int:
    # Asia/Seoul fixed offset
    tz = dt.timezone(dt.timedelta(hours=9))

    if len(sys.argv) >= 2:
        day = dt.date.fromisoformat(sys.argv[1])
    else:
        day = dt.datetime.now(tz).date()

    day_start, day_end = _utc_day_range(day, tz)
    mtd_start, mtd_end = _utc_month_to_date_range(day, tz)

    day_cost = fetch_costs(day_start, day_end)
    mtd_cost = fetch_costs(mtd_start, mtd_end)

    out = {
        "date": day.isoformat(),
        "day": {"start_time": day_start, "end_time": day_end, "total_usd": day_cost.total_usd},
        "mtd": {"start_time": mtd_start, "end_time": mtd_end, "total_usd": mtd_cost.total_usd},
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
