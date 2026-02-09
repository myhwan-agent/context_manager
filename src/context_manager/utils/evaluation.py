from __future__ import annotations

import re


def compute_summary_length(summary: str) -> int:
    return len(summary or "")


def compute_action_count(plan: str) -> int:
    """Very rough action count.

    Counts bullet lines like:
    - [look] ...
    """

    if not plan:
        return 0
    return len(re.findall(r"^\s*-\s*\[[^\]]+\]", plan, flags=re.MULTILINE))
