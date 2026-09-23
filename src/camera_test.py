"""Quick webcam check: shows the live feed so we know which camera index works.

Usage:
    python src/camera_test.py      # tries camera 0
    python src/camera_test.py 1    # tries camera 1
Press q in the video window to quit.
"""
import sys

import cv2


def main():
    camera_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0

    # CAP_DSHOW = DirectShow backend. On Windows it opens the camera much faster
    # than the default backend (MSMF), which can hang for several seconds.
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"Could not open camera {camera_index}. Try another index, e.g. 1.")
        sys.exit(1)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera {camera_index} opened at {width}x{height}. Press q to quit.")

    while True:
        ok, frame = cap.read()  # frame is a NumPy array of shape (height, width, 3), BGR order
        if not ok:
            print("Failed to read a frame.")
            break

        cv2.imshow(f"Camera {camera_index}", frame)

        # waitKey(1) waits 1 ms for a key press and lets the window refresh.
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
