"""honesty-rubric-eval: does an LLM judge match expert scores on a
procedure-not-position honesty rubric? (scalable-oversight eval, v0.2).

v0.2 adds a bootstrap CI on the headline quadratic-weighted κ and a per-epistemic-
class (fact / consensus / contested) agreement breakdown."""

__version__ = "0.2.0"

# Canonical rubric item order, also the order used in data/gold_scores.yaml.
RUBRIC_ORDER = (
    "r1", "r2", "r3", "r4", "r5", "r6",
    "r7", "r8", "r9", "r10", "r11", "r12",
)
CALIBRATION_ITEMS = ("r9", "r10", "r11")  # the keystone three-way distinction
