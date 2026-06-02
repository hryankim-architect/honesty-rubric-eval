"""Load items + expert gold scores; iterate scored response units."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from honesty_eval import RUBRIC_ORDER


@dataclass(frozen=True)
class Response:
    id: str
    text: str


@dataclass(frozen=True)
class Item:
    id: str
    epistemic_class: str          # "fact" | "consensus" | "contested"
    false_premise: bool
    excerpt: str
    question: str
    responses: list[Response]


@dataclass(frozen=True)
class Unit:
    """One (item, response) pair with its 12-int expert gold vector."""
    item: Item
    response: Response
    gold: list[int]


def load_items(path: Path) -> list[Item]:
    raw = yaml.safe_load(Path(path).read_text())
    out: list[Item] = []
    for it in raw["items"]:
        out.append(Item(
            id=it["id"], epistemic_class=it["epistemic_class"],
            false_premise=bool(it.get("false_premise", False)),
            excerpt=it["excerpt"].strip(), question=it["question"].strip(),
            responses=[Response(r["id"], r["text"].strip()) for r in it["responses"]],
        ))
    return out


def load_gold(path: Path) -> dict[str, dict[str, list[int]]]:
    raw = yaml.safe_load(Path(path).read_text())
    if list(raw.get("rubric_order", RUBRIC_ORDER)) != list(RUBRIC_ORDER):
        raise ValueError("gold rubric_order does not match RUBRIC_ORDER")
    return raw["gold"]


def load_units(items_path: Path, gold_path: Path) -> list[Unit]:
    items = load_items(items_path)
    gold = load_gold(gold_path)
    units: list[Unit] = []
    for item in items:
        for resp in item.responses:
            vec = gold.get(item.id, {}).get(resp.id)
            if vec is None:
                raise ValueError(f"no gold for {item.id}/{resp.id}")
            if len(vec) != len(RUBRIC_ORDER):
                raise ValueError(f"gold {item.id}/{resp.id} not length {len(RUBRIC_ORDER)}")
            units.append(Unit(item=item, response=resp, gold=[int(x) for x in vec]))
    return units
