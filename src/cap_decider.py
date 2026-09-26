"""Turn the stream of per-frame answers into ONE decision per cap.

The model answers every frame (about 30 per second), and single frames can be wrong:
a hand entering the view, a cap still moving, an awkward angle. CapDecider watches
the answers over time and makes one stable decision per cap:

    WAITING      the spot is empty, waiting for a cap
        |  a frame that isn't "empty" arrives
        v
    COLLECTING   keep the last WINDOW answers, decide once one answer clearly wins.
        |        Votes only count while the picture is still: if something moves
        |        (a hand, the cap sliding into place), the votes so far are thrown away.
        |  a cap answer wins                  -> report the decision, go to DECIDED
        |  "empty" wins (nothing really placed) -> back to WAITING
        v
    DECIDED      the decision is made, wait until the spot is empty again
        |  EMPTY_TO_RESET empty frames in a row
        v
    WAITING      ready for the next cap

Run this file on its own to watch it work on two made-up scenarios:
    python src/cap_decider.py
"""
from collections import Counter, deque

WINDOW = 15  # how many recent frames vote (about half a second of video)
AGREEMENT = 12  # votes the winning answer needs out of WINDOW (80%)
EMPTY_TO_RESET = 10  # empty frames in a row that mean "the cap was taken away"


def majority(answers):
    """Return (most_common_answer, number_of_votes) for a list of answers.

    Example: majority(["good", "defective", "good"]) -> ("good", 2)
    """
    counter = Counter(answers)
    most_common_answer, number_of_votes = counter.most_common(1)[0]
    return most_common_answer, number_of_votes


class CapDecider:
    """Remembers recent answers between frames and makes one decision per cap."""

    def __init__(self):
        self.state = "WAITING"
        self.window = deque(maxlen=WINDOW)  # keeps only the last WINDOW answers
        self.empty_streak = 0  # how many "empty" answers in a row, right now

    def update(self, answer, moving=False):
        """Feed one frame's answer. Returns the cap's decision when it's made, otherwise None.

        `moving` is True when the picture changed a lot since the previous frame
        (measured in live.py), which means a hand or the cap is still moving.
        """
        if answer == "empty":
            self.empty_streak += 1
        else:
            self.empty_streak = 0

        if self.state == "WAITING":
            if answer != "empty":  # something arrived on the spot
                self.window.clear()
                self.window.append(answer)
                self.state = "COLLECTING"

        elif self.state == "COLLECTING":
            if moving:
                self.window.clear()
                return None
            self.window.append(answer)
            if len(self.window) == WINDOW:
                winner, votes = majority(list(self.window))
                if votes >= AGREEMENT:
                    if winner == "empty":
                        self.state = "WAITING"
                    else:
                        self.state = "DECIDED"
                        return winner

        elif self.state == "DECIDED":
            if self.empty_streak >= EMPTY_TO_RESET:
                self.state = "WAITING"

        return None


def repeat(answer, count, moving=False):
    """`count` identical frames, as (answer, moving) pairs. Example: repeat("empty", 10)."""
    return [(answer, moving)] * count


def run_scenario(title, frames, expected):
    """Feed (answer, moving) pairs to a fresh decider and print every state change."""
    print(f"\n=== {title} ===")
    decider = CapDecider()
    decisions = []
    for frame_number, (answer, moving) in enumerate(frames, start=1):
        previous_state = decider.state
        decision = decider.update(answer, moving)
        if decider.state != previous_state:
            motion = "(moving)" if moving else ""
            print(f"frame {frame_number:3}: {answer:9} {motion:8} -> {previous_state} to {decider.state}")
        if decision is not None:
            decisions.append(decision)
            print(f"           CAP DECIDED: {decision.upper()}")
    print(f"Decisions: {decisions}  (expected: {expected})")


def demo():
    """Two made-up scenarios: caps placed quickly, and a good cap placed slowly."""
    run_scenario(
        "Two caps placed quickly",
        repeat("empty", 10)  # spot empty
        + [("good", False), ("defective", False), ("defective", False), ("good", False)]  # hand brings cap 1
        + repeat("defective", 20)  # the cap sits on the spot
        + repeat("empty", 12)  # the cap is taken away
        + [("defective", False), ("good", False), ("good", False)]  # hand brings cap 2
        + repeat("good", 20)  # the cap sits on the spot
        + repeat("empty", 12),  # taken away
        expected=["defective", "good"],
    )
    run_scenario(
        "A good cap placed slowly (hand in view for 20 frames)",
        repeat("empty", 10)  # spot empty
        + repeat("defective", 20, moving=True)  # the moving hand makes frames look defective
        + repeat("good", 20)  # hand gone, cap settled and still
        + repeat("empty", 12),  # taken away
        expected=["good"],
    )


if __name__ == "__main__":
    demo()
