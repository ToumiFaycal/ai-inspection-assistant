"""Grade the assistant on its exam (assistant_eval_cases.py) and print its score.

Each question is asked in a fresh conversation, the answer is graded automatically, and
the results are printed per category and saved to runs/assistant_eval/. The questions are
about a demo log built in a temporary folder: the real inspection log is never touched.

Needs Ollama running with qwen3:8b and embeddinggemma. Takes a few minutes.

Usage:
    python src/evaluate_assistant.py
"""
import json
import re
import tempfile
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from numpy import number

import assistant
import assistant_tools
from assistant import SYSTEM_PROMPT, answer_question, find_citations
from assistant_eval_cases import CASES, demo_rows
from inspection_log import open_log

RESULTS_DIR = Path(__file__).resolve().parent.parent / "runs" / "assistant_eval"


def score_answer(answer, case):
    """Grade one answer. Returns (passed, reasons): reasons lists what was wrong, [] if nothing.

    `case` is one dict from CASES, which may have "must_include", "must_include_one_of",
    "must_include_numbers" and "must_cite_one_of" (see the top of assistant_eval_cases.py).
    """
    reasons = []  # must exist BEFORE anything is added to it
    text_of_answer = answer.lower()  # compare in lowercase, so capital letters don't matter

    must_include = [text.lower() for text in case.get("must_include", [])]
    must_include_one_of = [text.lower() for text in case.get("must_include_one_of", [])]
    must_include_numbers = [float(n) for n in case.get("must_include_numbers", [])]
    must_cite_one_of = [text.lower() for text in case.get("must_cite_one_of", [])]

    for text in must_include:
        if text not in text_of_answer:
            reasons.append(f"missing {text!r}")

    if must_include_one_of and not any(text in text_of_answer for text in must_include_one_of):
        reasons.append(f"none of {must_include_one_of}")

    numbers = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", answer)]
    for number in must_include_numbers:
        if number not in numbers:
            reasons.append(f"missing the number {number}")

    citations = [citation.lower() for citation in find_citations(answer)]  # lowercase too, like the rule
    if must_cite_one_of and not any(section in citations for section in must_cite_one_of):
        reasons.append(f"no citation of {must_cite_one_of}")

    return (len(reasons) == 0, reasons)


def build_demo_log(folder):
    """Create the demo log in `folder` and point the assistant's tools at it."""
    db_path = Path(folder) / "demo_inspections.db"
    connection = open_log(db_path)
    connection.executemany(
        "INSERT INTO inspections (timestamp, decision, confidence, reason) VALUES (?, ?, ?, ?)",
        demo_rows(),
    )
    connection.commit()
    connection.close()
    assistant_tools.DB_PATH = db_path  # the tools now read the demo log
    return db_path


def main():
    assistant.SHOW_TOOL_CALLS = False
    results = []
    with tempfile.TemporaryDirectory() as folder:  # deleted automatically at the end
        build_demo_log(folder)
        print(f"Asking {len(CASES)} questions (the first answer is slow while the models load)...\n")
        for number, case in enumerate(CASES, start=1):
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]  # a fresh conversation
            started = time.time()
            answer = answer_question(messages, case["question"])
            seconds = time.time() - started
            passed, reasons = score_answer(answer, case) or (False, ["score_answer returned nothing"])
            results.append({**case, "answer": answer, "citations": find_citations(answer) or [],
                            "passed": passed, "reasons": reasons, "seconds": round(seconds, 1)})
            print(f"{number:2}. {'PASS' if passed else 'FAIL'}  [{case['category']}] {case['question']}  ({seconds:.1f} s)")
            if not passed:
                print(f"      why:    {'; '.join(reasons)}")
                print(f"      answer: {answer}")

    print("\nScore per category:")
    by_category = defaultdict(list)
    for result in results:
        by_category[result["category"]].append(result["passed"])
    for category, outcomes in by_category.items():
        print(f"  {category:12} {sum(outcomes)}/{len(outcomes)}")
    total = sum(result["passed"] for result in results)
    print(f"  {'TOTAL':12} {total}/{len(results)} = {100 * total / len(results):.1f}%")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"results_{datetime.now():%Y%m%d_%H%M%S}.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nEvery question, answer and grade saved to {out_path}")


if __name__ == "__main__":
    main()
