"""Turn the stream of per-frame answers into ONE decision per cap.

The model answers every frame (about 30 per second), and single frames can be wrong:
a hand entering the view, a cap still moving, an awkward angle. CapDecider watches
the answers over time and makes one stable decision per cap:

    WAITING      the spot is empty, waiting for a cap
        |  a frame that isn't "empty" arrives
        v
    COLLECTING   keep the last WINDOW answers, decide once one answer clearly wins
        |  a cap answer wins                  -> report the decision, go to DECIDED
        |  "empty" wins (nothing really placed) -> back to WAITING
        v
    DECIDED      the decision is made, wait until the spot is empty again
        |  EMPTY_TO_RESET empty frames in a row
        v
    WAITING      ready for the next cap

Run this file on its own to watch it work on a made-up sequence of answers:
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

    def update(self, answer):
        """Feed one frame's answer. Returns the cap's decision when it's made, otherwise None."""
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


def demo():
    """Feed a made-up sequence of answers and print what the decider does."""
    sequence = (
        ["empty"] * 10  # spot empty
        + ["good", "defective", "defective", "good"]  # a hand brings the first cap
        + ["defective"] * 20  # the cap sits on the spot
        + ["empty"] * 12  # the cap is taken away
        + ["defective", "good", "good"]  # a hand brings the second cap
        + ["good"] * 20  # the cap sits on the spot
        + ["empty"] * 12  # taken away
    )
    decider = CapDecider()
    decisions = []
    for frame_number, answer in enumerate(sequence, start=1):
        previous_state = decider.state
        decision = decider.update(answer)
        if decider.state != previous_state:
            print(f"frame {frame_number:3}: {answer:9} -> {previous_state} to {decider.state}")
        if decision is not None:
            decisions.append(decision)
            print(f"           CAP DECIDED: {decision.upper()}")
    print(f"\nDecisions: {decisions}  (expected: ['defective', 'good'])")


if __name__ == "__main__":
    demo()
