"""Train the cap classifier (good / defective / empty) on data/caps.

Fine-tunes a small YOLO classification model that was pretrained on ImageNet.
Training uses data/caps/train, checks itself on data/caps/val after every epoch,
and never touches data/caps/test (that is for the final evaluation only).

Results (weights, plots, metrics) go to runs/<RUN_NAME>/.

Usage:
    python src/train.py
"""
from pathlib import Path

from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "caps"  # contains train/, val/ and test/
RUNS_DIR = PROJECT_ROOT / "runs"

BASE_MODEL = "yolo26n-cls.pt"  # newest nano classification model, pretrained on ImageNet
RUN_NAME = "baseline"  # change it for each new experiment, so old results are kept


def main():
    model = YOLO(BASE_MODEL)
    model.train(data=str(DATA_DIR), epochs=50, imgsz=224, batch=16, patience=10, seed=0, device=0, project=str(RUNS_DIR), name=RUN_NAME, exist_ok=True)
    print(f"Best weights saved to: {model.trainer.best}")


if __name__ == "__main__":
    main()
