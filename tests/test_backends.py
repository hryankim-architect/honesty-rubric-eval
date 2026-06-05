"""Tests for backends.ollama_complete — the HTTP call is mocked, no server needed.

We assert the request shape (endpoint, model, prompt, deterministic temperature=0)
and that the `response` field is parsed out, so the judge's only external
dependency is covered without standing up Ollama.
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from honesty_eval.backends import ollama_complete  # noqa: E402


class _FakeResp:
    def __init__(self, payload: bytes):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._payload


def test_ollama_complete_parses_response_and_builds_request(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _FakeResp(json.dumps({"response": "hello world"}).encode("utf-8"))

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    complete = ollama_complete("qwen2.5:7b", host="http://localhost:11434")
    assert complete("score this") == "hello world"
    assert captured["url"].endswith("/api/generate")
    assert captured["body"]["model"] == "qwen2.5:7b"
    assert captured["body"]["prompt"] == "score this"
    assert captured["body"]["stream"] is False
    assert captured["body"]["options"]["temperature"] == 0


def test_ollama_complete_missing_response_key_returns_empty(monkeypatch):
    def fake_urlopen(req, timeout=None):
        return _FakeResp(json.dumps({"other": "x"}).encode("utf-8"))

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert ollama_complete("m")("p") == ""        # .get("response", "") default
