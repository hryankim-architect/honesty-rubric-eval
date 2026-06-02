#!/usr/bin/env python3
"""CI gate: fail if CJK characters appear in committed text artifacts.

Public artifacts ship in English (portfolio R6 convention). Scans tracked text
files and exits non-zero if any CJK codepoint is found. Paths listed in
`scripts/english-only.skip` (one per line) are exempt.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXTS = {".md", ".py", ".yaml", ".yml", ".toml", ".txt"}


def _is_cjk(ch: str) -> bool:
    o = ord(ch)
    return (
        0x3040 <= o <= 0x30FF       # hiragana/katakana
        or 0x3400 <= o <= 0x4DBF    # CJK ext A
        or 0x4E00 <= o <= 0x9FFF    # CJK unified
        or 0xAC00 <= o <= 0xD7A3    # hangul syllables
        or 0x1100 <= o <= 0x11FF    # hangul jamo
    )


def main() -> int:
    skip_file = REPO / "scripts" / "english-only.skip"
    skips = set()
    if skip_file.exists():
        skips = {s.strip() for s in skip_file.read_text().splitlines() if s.strip()}
    bad: list[str] = []
    for p in REPO.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in EXTS:
            continue
        rel = p.relative_to(REPO).as_posix()
        if any(part in {".git", ".venv", "__pycache__"} for part in p.parts):
            continue
        if rel in skips:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(_is_cjk(ch) for ch in text):
            bad.append(rel)
    if bad:
        sys.stderr.write("::error::CJK characters found in: " + ", ".join(sorted(bad)) + "\n")
        return 1
    print("english-only: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
