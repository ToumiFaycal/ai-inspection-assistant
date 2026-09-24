"""Shared camera settings and helper, used by every script that needs the camera."""
import cv2

# Phone running the IP Webcam app on the same Wi-Fi. If the phone gets a new IP,
# change it here (the app shows its address when you tap "Start server").
# Use a number instead (e.g. 0) for a webcam plugged into the laptop.
CAMERA_SOURCE = "http://192.168.100.5:8080/video"


def open_camera(source=CAMERA_SOURCE):
    """Open a local webcam (int index) or a network stream (URL string)."""
    if isinstance(source, int):
        # DirectShow opens local webcams quickly on Windows.
        return cv2.VideoCapture(source, cv2.CAP_DSHOW)
    # For a URL, let OpenCV pick the backend (it uses FFmpeg for network streams).
    return cv2.VideoCapture(source)
