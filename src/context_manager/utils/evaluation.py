from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvalResult:
    name: str
    score: float
    notes: str = ""


def simple_length_score(text: str, *, target: int = 2000) -> EvalResult:
    """Toy evaluation: penalize contexts that are too long.

    Real eval will be task-specific (plan success rate, action accuracy, etc.).
    """

    n = len(text)
    score = max(0.0, 1.0 - abs(n - target) / max(target, 1))
    return EvalResult(name="length_score", score=score, notes=f"len={n} target={target}")
