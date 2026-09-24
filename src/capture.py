"""Dataset capture tool: live camera preview, one key press saves the current frame
into data/caps/<SPLIT>/<class>/.

Keys:  g = good   d = defective   e = empty   q = quit

Set SPLIT before each photo session. A given physical cap is photographed in ONE
split only, so the model is never tested on a cap it has already seen in training.
"""
import sys
from datetime import datetime
from pathlib import Path

import cv2

from camera import CAMERA_SOURCE, open_camera

SPLIT = "train"  # "train", "val" or "test": change before each photo session

# Project root = the folder above src/, so the script works from any terminal folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "caps"

CLASSES = ["good", "defective", "empty"]
KEYS = {ord("g"): "good", ord("d"): "defective", ord("e"): "empty"}


def make_folders():
    """Create data/caps/<SPLIT>/<class>/ for every class. No error if they already exist."""
    for class_name in CLASSES:
        (DATA_DIR / SPLIT / class_name).mkdir(parents=True, exist_ok=True)


def unique_filename(label):
    """Return a filename for a new photo of `label`, e.g. "good_20260923_153012_123456.jpg"."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{label}_{stamp}.jpg"


def save_frame(frame, label):
    """Save `frame` into its class folder, then print how many photos each class has in SPLIT."""
    local_path = DATA_DIR / SPLIT / label / unique_filename(label)
    if not cv2.imwrite(str(local_path), frame):
        print(f"Warning: failed to save {local_path}")
        return
    print(f"Saved {local_path.name} | {SPLIT}: " +
          " ".join(f"{class_name}={len(list((DATA_DIR / SPLIT / class_name).glob('*.jpg')))}" for class_name in CLASSES))


def main():
    if SPLIT not in ("train", "val", "test"):
        sys.exit(f"SPLIT must be 'train', 'val' or 'test', got {SPLIT!r}")

    make_folders()

    cap = open_camera()
    if not cap.isOpened():
        sys.exit(f"Could not open camera {CAMERA_SOURCE}.")

    print(f"Saving into {DATA_DIR / SPLIT}")
    print("Keys: g = good, d = defective, e = empty, q = quit")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read a frame.")
            break

        # Draw the help text on a COPY. The saved photo must stay clean, otherwise
        # the text would end up in the training data.
        preview = frame.copy()
        cv2.putText(preview, f"SPLIT: {SPLIT}   g/d/e = save   q = quit", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow("Capture", preview)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key in KEYS:
            save_frame(frame, KEYS[key])

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
