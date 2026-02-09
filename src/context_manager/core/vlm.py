from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any, Optional, Protocol


@dataclass(frozen=True)
class VLMResponse:
    text: str
    meta: dict[str, Any] | None = None


class VLMClient(Protocol):
    """Protocol for a VLM client."""

    def generate(self, prompt: str, *, meta: dict[str, Any] | None = None) -> VLMResponse:  # pragma: no cover
        ...


@dataclass
class OpenAICompatibleClient:
    """A tiny OpenAI-API-shaped client wrapper.

    Intention:
    - We will point this at your GPU server later (base_url = http://<ip>:<port>)
    - The server should expose OpenAI-compatible endpoints.

    This wrapper uses only stdlib (urllib) to avoid extra dependencies.

    Environment variables (optional):
    - OPENAI_BASE_URL
    - OPENAI_API_KEY
    - OPENAI_MODEL
    """

    base_url: str = ""
    api_key: str = ""
    model: str = ""
    timeout_s: float = 60.0

    def __post_init__(self) -> None:
        if not self.base_url:
            self.base_url = os.getenv("OPENAI_BASE_URL", "").rstrip("/")
        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY", "")
        if not self.model:
            self.model = os.getenv("OPENAI_MODEL", "")

    def generate(self, prompt: str, *, meta: dict[str, Any] | None = None) -> VLMResponse:
        """Call an OpenAI-compatible server.

        We use the Responses API shape first; many proxies implement it.
        If your server exposes only /v1/chat/completions, we can add a fallback.
        """

        if not self.base_url:
            raise ValueError("base_url is required (set OPENAI_BASE_URL or pass base_url=...)")
        if not self.model:
            raise ValueError("model is required (set OPENAI_MODEL or pass model=...)")

        url = f"{self.base_url}/v1/responses"

        payload: dict[str, Any] = {
            "model": self.model,
            "input": prompt,
        }
        if meta:
            payload["metadata"] = meta

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        if self.api_key:
            req.add_header("Authorization", f"Bearer {self.api_key}")

        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            raw = resp.read().decode("utf-8")

        obj = json.loads(raw)

        # Responses API: text can appear in output[0].content[*].text
        text = _extract_response_text(obj)
        return VLMResponse(text=text, meta={"raw": obj})


def _extract_response_text(obj: dict[str, Any]) -> str:
    """Best-effort extraction for OpenAI Responses API."""

    try:
        output = obj.get("output") or []
        for item in output:
            content = item.get("content") or []
            for c in content:
                if c.get("type") == "output_text" and "text" in c:
                    return c["text"]
    except Exception:
        pass

    # Fallbacks
    if "text" in obj and isinstance(obj["text"], str):
        return obj["text"]
    if "output_text" in obj and isinstance(obj["output_text"], str):
        return obj["output_text"]
    return json.dumps(obj)[:2000]
