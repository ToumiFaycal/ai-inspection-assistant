"""Tests for src/preprocess.py: cropping a frame to the inspection square."""
import numpy as np

from preprocess import crop_roi


def test_landscape_frame_becomes_its_central_square():
    frame = np.zeros((720, 1280, 3), np.uint8)  # a black 1280x720 frame, like the phone's
    frame[:, 280] = 255  # paint the first column that should be kept white...
    frame[:, 999] = 255  # ...and the last one

    square = crop_roi(frame)

    assert square.shape == (720, 720, 3)
    assert square[0, 0, 0] == 255  # the crop starts exactly at column 280
    assert square[0, -1, 0] == 255  # and ends exactly at column 999


def test_portrait_frame_becomes_a_square():
    assert crop_roi(np.zeros((1280, 720, 3), np.uint8)).shape == (720, 720, 3)


def test_square_frame_is_kept_whole():
    assert crop_roi(np.zeros((500, 500, 3), np.uint8)).shape == (500, 500, 3)
