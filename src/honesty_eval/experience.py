"""Temporal split + exemplar retrieval for the experience-accumulating judge.

Arrival order (the order items appear in items.yaml) is the temporal axis.
Earlier items are the *experience pool*; later items are *held-out*. Retrieval
returns same-epistemic-class exemplars from the experience pool only — never the
held-out item itself — so few-shot grounding cannot leak the answer.
"""
from __future__ import annotations

from honesty_eval.dataset import Item, Unit


def temporal_split(units: list[Unit], items: list[Item],
                   n_experience_items: int) -> tuple[list[Unit], list[Unit]]:
    """Split units at the *item* level by arrival order.

    Returns (experience_units, holdout_units). Splitting by item (not by unit)
    guarantees no response of a held-out item sits in the experience pool.
    """
    order = [it.id for it in items]
    exp_ids = set(order[:n_experience_items])
    experience = [u for u in units if u.item.id in exp_ids]
    holdout = [u for u in units if u.item.id not in exp_ids]
    return experience, holdout


def retrieve_exemplars(holdout_item: Item, experience_units: list[Unit],
                       k: int) -> list[Unit]:
    """Up to k same-class exemplars from the experience pool, most-recent first.

    Never returns a unit from the held-out item itself (leakage guard).
    """
    same = [
        u for u in experience_units
        if u.item.epistemic_class == holdout_item.epistemic_class
        and u.item.id != holdout_item.id
    ]
    return list(reversed(same))[:k]  # experience_units are in arrival order
