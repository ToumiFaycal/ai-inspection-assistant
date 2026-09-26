"""Live inspection: classify every camera frame, then make one stable decision per cap.

Each frame goes through the same steps as the training photos:
    camera frame -> crop_roi (central square) -> model -> 3 probabilities -> decide -> answer
Each frame is also compared with the previous one to measure motion: while a hand or
the cap is moving, frames can't be trusted. The answers and the "moving" flag go to
CapDecider, which waits for still frames that agree and makes one decision per cap
(see cap_decider.py). Every decision is saved in the database (see inspection_log.py).

The window shows the cropped square, so you see exactly what the model sees:
    top:    this frame's answer and P(defective)
    middle: the decider's state (WAITING / COLLECTING / DECIDED) and the motion level
    bottom: the last cap's decision and the totals so far

Usage:
    python src/live.py      (click the window, then press q to quit)
"""
import sys
from collections import Counter

import cv2
import numpy as np

from camera import CAMERA_SOURCE, open_camera
from cap_decider import CapDecider
from classifier import IMAGE_SIZE, decide, load_model, probabilities
from inspection_log import DB_PATH, log_decision, open_log
from preprocess import crop_roi

# Text colour for each answer, in BGR order (OpenCV's colour order)
COLORS = {"good": (0, 180, 0), "defective": (0, 0, 255), "empty": (160, 160, 160)}
FONT = cv2.FONT_HERSHEY_SIMPLEX

# Average change per pixel between two frames (0-255) above which the picture counts
# as "moving". A still scene measured about 1.3. Adjust from the numbers on screen.
MOTION_THRESHOLD = 3.0


def small_gray(image):
    """Shrink an image to 160x160 grey, so comparing frames is fast and ignores tiny details."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.resize(gray, (160, 160)).astype(np.float32)  # float: see motion_between


def motion_between(previous, current):
    """Average brightness change per pixel between two small grey images (0 = identical)."""
    # The images are floats, not uint8: with uint8, 3 - 5 would wrap around to 254.
    return float(np.abs(current - previous).mean())


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
    log = open_log()  # the database connection, open for the whole session
    print(f"Saving decisions to {DB_PATH}")

    decider = CapDecider()
    totals = Counter()  # decisions so far, per class
    last_decision = None
    last_reason = None  # "vote" or "unsure"
    previous_small = None  # the previous frame, shrunk, to measure motion

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read a frame.")
            break

        answer, probs, roi = classify_frame(model, frame)

        small = small_gray(roi)
        motion = 0.0 if previous_small is None else motion_between(previous_small, small)
        previous_small = small
        moving = motion > MOTION_THRESHOLD

        decision = decider.update(answer, moving)
        if decision is not None:
            last_decision, last_reason = decision, decider.reason
            confidence = decider.agreement(decision)
            log_decision(log, decision, confidence, last_reason)
            totals[decision] += 1
            print(f"Cap #{sum(totals.values())}: {decision.upper()} "
                  f"(confidence {confidence:.2f}, reason: {last_reason}) - saved")

        preview = roi.copy()  # draw on a copy: the same clean-image habit as in capture.py
        height = preview.shape[0]
        put_text(preview, f"frame: {answer}  P(defective) = {probs['defective']:.2f}", (15, 35), 0.8, COLORS[answer])
        put_text(preview, decider.state, (15, 75), 0.8, (255, 255, 255))
        motion_color = (0, 200, 255) if moving else (255, 255, 255)  # orange while moving
        put_text(preview, f"motion {motion:.1f} ({'moving' if moving else 'still'})", (15, 110), 0.7, motion_color)
        if last_decision is not None:
            if last_reason == "unsure":
                put_text(preview, "unsure: check this cap by hand", (15, height - 100), 0.8, COLORS["defective"])
            put_text(preview, f"LAST CAP: {last_decision.upper()}", (15, height - 55), 1.3, COLORS[last_decision], 3)
        put_text(preview, f"good {totals['good']}   defective {totals['defective']}", (15, height - 18),
                 0.8, (255, 255, 255))
        cv2.imshow("Live inspection", preview)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    log.close()


if __name__ == "__main__":
    main()
