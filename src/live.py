"""Live inspection, part 1: classify every camera frame and show the answer on screen.

Each frame goes through the same steps as the training photos:
    camera frame -> crop_roi (central square) -> model -> 3 probabilities -> decide -> answer
The window shows the cropped square, so you see exactly what the model sees.

Usage:
    python src/live.py      (click the window, then press q to quit)
"""
import sys

import cv2

from camera import CAMERA_SOURCE, open_camera
from classifier import IMAGE_SIZE, decide, load_model, probabilities
from preprocess import crop_roi

# Text colour for each answer, in BGR order (OpenCV's colour order)
COLORS = {"good": (0, 180, 0), "defective": (0, 0, 255), "empty": (160, 160, 160)}


def classify_frame(model, frame):
    """Classify one camera frame. Returns (answer, probs, roi)."""
    roi = crop_roi(frame)
    result = model.predict(roi, imgsz=IMAGE_SIZE, verbose=False)[0]  # one image in, one result out
    probs = probabilities(result)
    return decide(probs), probs, roi


def main():
    model = load_model()
    cap = open_camera()
    if not cap.isOpened():
        sys.exit(f"Could not open camera {CAMERA_SOURCE}.")
    print("Live inspection running. Click the window, then press q to quit.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read a frame.")
            break

        answer, probs, roi = classify_frame(model, frame)

        preview = roi.copy()  # draw on a copy: the same clean-image habit as in capture.py
        cv2.putText(preview, answer.upper(), (15, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLORS[answer], 3)
        cv2.putText(preview, f"P(defective) = {probs['defective']:.2f}", (15, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS[answer], 2)
        cv2.imshow("Live inspection", preview)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
