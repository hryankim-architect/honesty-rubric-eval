"""Tests for the hash-chained audit ledger: happy path + tamper detection.

The eval's own verdict is only trustworthy if its ledger is tamper-evident, so
the keystone test mutates a committed entry and asserts `verify` catches it (the
canary principle applied to the audit chain itself).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from honesty_eval import audit  # noqa: E402


def test_verify_missing_ledger_is_ok(tmp_path):
    assert audit.verify(tmp_path / "absent.ndjson") == (True, 0)


def test_verify_clean_chain(tmp_path):
    led = tmp_path / "led.ndjson"
    for i in range(3):
        audit.emit("act", "job", {"i": i}, ledger_path=led)
    assert audit.verify(led) == (True, 3)


def test_verify_detects_payload_tampering(tmp_path):
    led = tmp_path / "led.ndjson"
    for i in range(3):
        audit.emit("act", "job", {"i": i}, ledger_path=led)

    lines = led.read_text().splitlines()
    entry = json.loads(lines[0])
    entry["fields"]["i"] = 999                 # mutate a committed entry's payload
    lines[0] = json.dumps(entry)
    led.write_text("\n".join(lines) + "\n")

    ok, _ = audit.verify(led)
    assert ok is False                         # chain hash no longer matches


def test_emit_returns_entry_and_links_prev_hash(tmp_path):
    led = tmp_path / "led.ndjson"
    first = audit.emit("act", "job", {"i": 0}, ledger_path=led)
    second = audit.emit("act", "job", {"i": 1}, ledger_path=led)
    assert first["prev_hash"]                   # genesis link present
    assert second["prev_hash"] != first["prev_hash"]   # each entry advances the chain
