"""Image preprocessing shared by training and live inspection.

crop_roi() cuts a frame down to the region of interest (ROI): the central square
where the cap sits. Training photos and live camera frames go through the same
crop, so the model always sees the same kind of image.

Run this file once to write cropped copies of the whole dataset:
    python src/preprocess.py

    data/caps/      originals (1280x720), never modified
    data/caps_roi/  same split/class folders, square crops (720x720)
"""
from collections import Counter
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_ROOT / "data" / "caps"
OUTPUT_DIR = PROJECT_ROOT / "data" / "caps_roi"


def crop_roi(frame):
    """Return the central square of `frame`, as tall as the frame (1280x720 -> 720x720)."""
    height, width = frame.shape[:2] # frame.shape is (height, width, channels) and :2 takes the first two values, ignoring channels.
    side = min(height, width)
    y1 = (height - side) // 2
    y2 = y1 + side
    x1 = (width - side) // 2
    x2 = x1 + side
    return frame[y1:y2, x1:x2]


def main():
    counts = Counter()  # photos written per "split/class", to compare with the originals
    for src_path in sorted(SOURCE_DIR.glob("*/*/*.jpg")):  # <split>/<class>/<photo>.jpg
        relative = src_path.relative_to(SOURCE_DIR)  # e.g. train/good/good_2026....jpg
        out_path = OUTPUT_DIR / relative
        out_path.parent.mkdir(parents=True, exist_ok=True)

        frame = cv2.imread(str(src_path))
        if frame is None:
            print(f"Warning: could not read {src_path}")
            continue

        roi = crop_roi(frame)
        if not cv2.imwrite(str(out_path), roi): # incase the write fails, e.g. disk full, permission denied, etc.
            print(f"Warning: could not save {out_path}")
            continue
        counts[f"{relative.parts[0]}/{relative.parts[1]}"] += 1 # count how many photos were written into each split/class folder

    for folder, n in sorted(counts.items()): # display how many photos were written into each split/class folder, e.g. "train/good: 12"
        print(f"{folder}: {n}")
    print(f"Wrote {sum(counts.values())} cropped photos into {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
