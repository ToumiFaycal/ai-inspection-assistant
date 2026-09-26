"""The trained cap classifier and its decision rule, shared by evaluation and live inspection.

Everything that turns an image into an answer lives here, so evaluate.py and live.py
always use the same model, the same image size and the same threshold.
"""
from pathlib import Path

from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEIGHTS = PROJECT_ROOT / "runs" / "roi_square" / "weights" / "best.pt"  # the chosen model (v1)

CLASSES = ["good", "defective", "empty"]
IMAGE_SIZE = 224  # the size the model was trained at
DEFECT_THRESHOLD = 0.4  # chosen on val, frozen before the test run: don't change it


def load_model():
    """Load the chosen trained model from disk."""
    return YOLO(str(WEIGHTS))


def probabilities(result):
    """Turn one Ultralytics result into a dict like {"good": 0.03, "defective": 0.95, "empty": 0.02}."""
    # result.names maps class number -> name, e.g. {0: "defective", 1: "empty", 2: "good"}
    return {result.names[i]: float(p) for i, p in enumerate(result.probs.data.tolist())}


def decide(probs, threshold=DEFECT_THRESHOLD):
    """Turn the three probabilities into one answer: "good", "defective" or "empty"."""
    if probs["defective"] >= threshold:
        return "defective"
    elif probs["good"] > probs["empty"]:
        return "good"
    else:
        return "empty"
