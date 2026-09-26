"""Evaluate the trained cap classifier on one split of the dataset.

For every photo in data/caps_roi/<SPLIT>/<class>/, the model gives three probabilities
(good, defective, empty). A decision rule with a threshold on "defective" turns them
into one answer, and the answers are compared with the folder names.

Usage:
    python src/evaluate.py

"""
from pathlib import Path

from classifier import CLASSES, DEFECT_THRESHOLD, IMAGE_SIZE, WEIGHTS, decide, load_model, probabilities

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "caps_roi"

SPLIT = "val"  # "val" while choosing the threshold, "test" once at the very end


def predict_split(model, split):
    """Run the model on every photo of `split`.

    Returns a list of (path, true_class, probs) - true_class = the class folder the photo is in, where probs is a dict such as
    {"good": 0.03, "defective": 0.95, "empty": 0.02}.
    """
    rows = []
    for true_class in CLASSES:
        files = sorted((DATA_DIR / split / true_class).glob("*.jpg"))
        if not files:
            continue
        results = model.predict([str(f) for f in files], imgsz=IMAGE_SIZE, verbose=False)
        for path, result in zip(files, results): # zip() pairs each photo with its result
            rows.append((path, true_class, probabilities(result)))
    return rows


def confusion_matrix(rows, threshold):
    """Count the answers: matrix[true_class][predicted_class] = number of photos.

    Rows are the TRUE class (the folder), columns the PREDICTED class.
    (Ultralytics' confusion_matrix.png draws it the other way round.)
    """
    matrix = {t: {p: 0 for p in CLASSES} for t in CLASSES}
    for path, true_class, probs in rows:
        predicted_class = decide(probs, threshold)
        matrix[true_class][predicted_class] += 1
    return matrix


def precision_recall(matrix, cls):
    """Return (precision, recall) for one class, as numbers between 0 and 1."""
    correct = matrix[cls][cls]
    total_true = sum(matrix[cls][p] for p in CLASSES)
    total_predicted = sum(matrix[t][cls] for t in CLASSES)
    recall = correct / total_true if total_true > 0 else 0.0
    precision = correct / total_predicted if total_predicted > 0 else 0.0
    return precision, recall


def print_report(matrix):
    """Print the confusion matrix, precision and recall per class, and accuracy."""
    width = 11
    print("\nConfusion matrix (rows = true class, columns = model's answer)")
    print(" " * width + "".join(f"{p:>{width}}" for p in CLASSES))
    for t in CLASSES:
        print(f"{t:<{width}}" + "".join(f"{matrix[t][p]:>{width}}" for p in CLASSES))

    print(f"\n{'class':<{width}}{'precision':>{width}}{'recall':>{width}}")
    for cls in CLASSES:
        precision, recall = precision_recall(matrix, cls)
        print(f"{cls:<{width}}{precision:>{width}.1%}{recall:>{width}.1%}")

    correct = sum(matrix[c][c] for c in CLASSES)
    total = sum(matrix[t][p] for t in CLASSES for p in CLASSES)
    print(f"\nAccuracy: {correct}/{total} = {correct / total:.1%}")


def print_mistakes(rows, threshold):
    """List every photo whose answer differs from its folder, with the probabilities."""
    mistakes = [(path, true_class, probs) for path, true_class, probs in rows
                if decide(probs, threshold) != true_class]
    print(f"\nMistakes: {len(mistakes)}")
    for path, true_class, probs in mistakes:
        scores = "  ".join(f"{c} {probs[c]:.2f}" for c in CLASSES)
        print(f"  {true_class}/{path.name}: answered {decide(probs, threshold)}  ({scores})")


def print_threshold_table(rows):
    """Show how "defective" precision/recall change with the threshold (use on val only)."""
    print("\nThreshold table for 'defective' (choose DEFECT_THRESHOLD from this, on val)")
    print(f"{'threshold':>10}{'recall':>9}{'precision':>11}{'missed':>8}{'false alarms':>14}")
    for threshold in [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        matrix = confusion_matrix(rows, threshold)
        precision, recall = precision_recall(matrix, "defective")
        missed = sum(matrix["defective"][p] for p in CLASSES if p != "defective")
        false_alarms = sum(matrix[t]["defective"] for t in CLASSES if t != "defective")
        print(f"{threshold:>10.2f}{recall:>9.1%}{precision:>11.1%}{missed:>8}{false_alarms:>14}")


def main():
    if SPLIT not in ("val", "test"):
        raise SystemExit(f"SPLIT must be 'val' or 'test', got {SPLIT!r}")

    model = load_model()
    rows = predict_split(model, SPLIT)
    print(f"Model: {WEIGHTS}")
    print(f"Split: {SPLIT} ({len(rows)} photos), defect threshold: {DEFECT_THRESHOLD}")
    if SPLIT == "test":
        print("FINAL EVALUATION: report these numbers, don't tune anything based on them.")

    matrix = confusion_matrix(rows, DEFECT_THRESHOLD)
    print_report(matrix)
    print_mistakes(rows, DEFECT_THRESHOLD)
    if SPLIT == "val":  # never choose the threshold by looking at test, only by val
        print_threshold_table(rows)


if __name__ == "__main__":
    main()
