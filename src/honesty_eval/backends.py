"""LLM backends for the judge — dependency-free `complete(prompt) -> str` callables.

The real scalable-oversight measurement plugs one of these into `judge.LLMJudge`.
`ollama_complete` talks to a local Ollama server (the portfolio substrate already
serves Qwen / Gemma there); no extra Python dependency is required.
"""
from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable


def ollama_complete(model: str, host: str = "http://localhost:11434",
                    timeout: float = 180.0) -> Callable[[str], str]:
    """Return a complete(prompt)->str that calls a local Ollama /api/generate.

    Deterministic (temperature 0). Runs on the user's machine against a locally
    served model — not an external web fetch.
    """
    url = host.rstrip("/") + "/api/generate"

    def complete(prompt: str) -> str:
        payload = json.dumps({
            "model": model, "prompt": prompt, "stream": False,
            "options": {"temperature": 0},
        }).encode("utf-8")
        req = urllib.request.Request(  # noqa: S310 — local Ollama endpoint
            url, data=payload, headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8")).get("response", "")

    return complete
