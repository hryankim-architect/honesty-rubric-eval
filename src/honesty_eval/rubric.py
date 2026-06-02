"""Load the honesty rubric (12 items, 0/1/2 anchors)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from honesty_eval import RUBRIC_ORDER


@dataclass(frozen=True)
class RubricItem:
    id: str
    name: str
    group: str
    anchors: dict[int, str]


def load_rubric(path: Path) -> list[RubricItem]:
    """Return the 12 rubric items in canonical RUBRIC_ORDER."""
    raw = yaml.safe_load(Path(path).read_text())
    items: dict[str, RubricItem] = {}
    for group, entries in raw["groups"].items():
        for e in entries:
            items[e["id"]] = RubricItem(
                id=e["id"], name=e["name"], group=group,
                anchors={int(k): v for k, v in e["anchors"].items()},
            )
    missing = [r for r in RUBRIC_ORDER if r not in items]
    if missing:
        raise ValueError(f"rubric missing items: {missing}")
    return [items[r] for r in RUBRIC_ORDER]
