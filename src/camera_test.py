"""Quick camera check: shows the live feed so we can check the camera works.

Usage:
    python src/camera_test.py        # the default camera from camera.py (the phone)
    python src/camera_test.py 0      # laptop webcam, by index
    python src/camera_test.py http://192.168.100.5:8080/video   # any stream URL
Press q in the video window to quit.
"""
import sys

import cv2

from camera import CAMERA_SOURCE, open_camera


def main():
    source = sys.argv[1] if len(sys.argv) > 1 else CAMERA_SOURCE
    if isinstance(source, str) and source.isdigit():
        source = int(source)  # "0" typed in the terminal is text: turn it into the number 0

    cap = open_camera(source)
    if not cap.isOpened():
        print(f"Could not open camera {source}.")
        sys.exit(1)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera {source} opened at {width}x{height}. Press q to quit.")

    while True:
        ok, frame = cap.read()  # frame is a NumPy array of shape (height, width, 3), BGR order
        if not ok:
            print("Failed to read a frame.")
            break

        cv2.imshow("Camera test", frame)

        # waitKey(1) waits 1 ms for a key press and lets the window refresh.
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
