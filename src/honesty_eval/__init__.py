"""honesty-rubric-eval: does an LLM judge match expert scores on a
procedure-not-position honesty rubric? (scalable-oversight eval, v0.1)."""

__version__ = "0.1.0"

# Canonical rubric item order, also the order used in data/gold_scores.yaml.
RUBRIC_ORDER = (
    "r1", "r2", "r3", "r4", "r5", "r6",
    "r7", "r8", "r9", "r10", "r11", "r12",
)
CALIBRATION_ITEMS = ("r9", "r10", "r11")  # the keystone three-way distinction
