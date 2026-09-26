"""Live inspection: classify every camera frame, then make one stable decision per cap.

Each frame goes through the same steps as the training photos:
    camera frame -> crop_roi (central square) -> model -> 3 probabilities -> decide -> answer
The frame answers then go to CapDecider, which waits for them to agree and makes
one decision per cap (see cap_decider.py).

The window shows the cropped square, so you see exactly what the model sees:
    top:    this frame's answer and P(defective)
    middle: the decider's state (WAITING / COLLECTING / DECIDED)
    bottom: the last cap's decision and the totals so far

Usage:
    python src/live.py      (click the window, then press q to quit)
"""
import sys
from collections import Counter

import cv2

from camera import CAMERA_SOURCE, open_camera
from cap_decider import CapDecider
from classifier import IMAGE_SIZE, decide, load_model, probabilities
from preprocess import crop_roi

# Text colour for each answer, in BGR order (OpenCV's colour order)
COLORS = {"good": (0, 180, 0), "defective": (0, 0, 255), "empty": (160, 160, 160)}
FONT = cv2.FONT_HERSHEY_SIMPLEX


def put_text(image, text, position, scale, color, thickness=2):
    """Write text with a dark outline, so it stays readable on light paper and dark caps alike."""
    cv2.putText(image, text, position, FONT, scale, (0, 0, 0), thickness + 3)  # thick dark outline
    cv2.putText(image, text, position, FONT, scale, color, thickness)  # the text itself, on top


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

    decider = CapDecider()
    totals = Counter()  # decisions so far, per class
    last_decision = None

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read a frame.")
            break

        answer, probs, roi = classify_frame(model, frame)
        decision = decider.update(answer)
        if decision is not None:
            last_decision = decision
            totals[decision] += 1
            print(f"Cap #{sum(totals.values())}: {decision.upper()}")

        preview = roi.copy()  # draw on a copy: the same clean-image habit as in capture.py
        height = preview.shape[0]
        put_text(preview, f"frame: {answer}  P(defective) = {probs['defective']:.2f}", (15, 35), 0.8, COLORS[answer])
        put_text(preview, decider.state, (15, 75), 0.8, (255, 255, 255))
        if last_decision is not None:
            put_text(preview, f"LAST CAP: {last_decision.upper()}", (15, height - 55), 1.3, COLORS[last_decision], 3)
        put_text(preview, f"good {totals['good']}   defective {totals['defective']}", (15, height - 18),
                 0.8, (255, 255, 255))
        cv2.imshow("Live inspection", preview)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
