from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Prompt:
    """A minimal prompt container.

    We keep this tiny on purpose; later we can add versioning, variables,
    and prompt registry.
    """

    name: str
    text: str
