"""Tests for src/cap_decider.py: one stable decision per cap."""
from cap_decider import CapDecider, majority, repeat


def decisions_for(frames):
    """Feed (answer, moving) frames to a fresh CapDecider and return the
    (decision, reason) pairs it made, e.g. [("defective", "vote")]."""
    decider = CapDecider()
    made = []
    for answer, moving in frames:
        decision = decider.update(answer, moving)
        if decision is not None:
            made.append((decision, decider.reason))
    return made


def test_majority_returns_the_winner_and_its_votes():
    assert majority(["good", "defective", "good"]) == ("good", 2)


def test_caps_placed_quickly():
    frames = (
        repeat("empty", 10)  # spot empty
        + [("good", False), ("defective", False), ("defective", False), ("good", False)]  # hand brings cap 1
        + repeat("defective", 20)  # cap 1 sits on the spot
        + repeat("empty", 12)  # cap 1 is taken away
        + [("defective", False), ("good", False), ("good", False)]  # hand brings cap 2
        + repeat("good", 20)  # cap 2 sits on the spot
        + repeat("empty", 12)  # cap 2 is taken away
    )
    assert decisions_for(frames) == [("defective", "vote"), ("good", "vote")]


def test_slow_placement_waits_until_the_picture_is_still():
    frames = (
        repeat("empty", 10)
        + repeat("defective", 20, moving=True)  # the moving hand makes frames look defective
        + repeat("good", 20)  # hand gone, cap settled and still
        + repeat("empty", 12)
    )
    assert decisions_for(frames) == [("good", "vote")]


def test_borderline_cap_is_rejected_as_unsure():
    frames = (
        repeat("empty", 10)
        + [("good", False), ("defective", False)] * 40  # 80 still frames that never agree
        + repeat("empty", 12)
    )
    assert decisions_for(frames) == [("defective", "unsure")]


def test_hand_over_the_empty_spot_decides_nothing():
    frames = (
        repeat("empty", 10)
        + repeat("defective", 5, moving=True)  # a hand passes over the spot
        + repeat("empty", 20)  # nothing was left: enough empty frames for "empty" to win the vote
    )
    assert decisions_for(frames) == []


def test_decider_is_ready_again_after_a_hand_passes():
    decider = CapDecider()
    for answer, moving in repeat("empty", 10) + repeat("defective", 5, moving=True) + repeat("empty", 20):
        decider.update(answer, moving)
    assert decider.state == "WAITING"  # not stuck in COLLECTING: the next cap will be seen
