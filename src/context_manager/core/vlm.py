from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class VLMResponse:
    text: str
    meta: dict[str, Any] | None = None


class VLMClient(Protocol):
    """Protocol for a VLM client.

    This repo's goal is *context management*, so the concrete VLM implementation
    is intentionally abstracted.
    """

    def generate(self, prompt: str, *, meta: dict[str, Any] | None = None) -> VLMResponse:  # pragma: no cover
        ...
