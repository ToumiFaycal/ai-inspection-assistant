"""The assistant's exam: questions with known correct answers, and the demo log they're about.

The demo log is rebuilt for every run, with dates counted from today, so questions about
"yesterday" or "today" always have the same answers:

    3 days ago  14:00:00 good, 14:01:30 good, 14:03:00 defective, 14:05:10 good, 14:06:45 good
    yesterday   09:15:00 good, 09:16:20 defective, 09:18:05 good, 09:20:40 good, 09:22:10 defective,
                09:25:00 good, 10:40:00 defective (unsure), 10:42:30 good, 10:45:15 good, 10:47:00 defective
    today       08:30:00 good, 08:31:40 good, 08:33:20 defective

    -> 18 caps: 12 good, 6 defective, 1 unsure reject.
       Yesterday: 10 caps, 6 good, 4 defective (40.0%), from 09:15:00 to 10:47:00.
       3 days ago: 5 caps, 1 defective (20.0%). Today: 3 caps, 1 defective (33.3%).

How an answer is graded (see score_answer in evaluate_assistant.py):
    must_include         every one of these texts must appear in the answer
    must_include_one_of  at least one of these texts must appear
    must_include_numbers every one of these numbers must appear as a whole number: 6 matches
                         "6 caps" but not "16 caps", and 40 matches "40.0%"
    must_cite_one_of     at least one of these document sections must be cited, as [Document > Section]
Texts are compared without caring about capital letters. Times are written without a leading
zero ("9:15"), so they match both "9:15" and "09:15".
"""
from datetime import date, timedelta


def demo_rows(today=None):
    """The demo log as (timestamp, decision, confidence, reason) rows, dated from `today`."""
    today = today or date.today()
    day = {"3 days ago": today - timedelta(days=3), "yesterday": today - timedelta(days=1), "today": today}
    caps = [
        ("3 days ago", "14:00:00", "good", 1.0, "vote"),
        ("3 days ago", "14:01:30", "good", 1.0, "vote"),
        ("3 days ago", "14:03:00", "defective", 1.0, "vote"),
        ("3 days ago", "14:05:10", "good", 0.93, "vote"),
        ("3 days ago", "14:06:45", "good", 1.0, "vote"),
        ("yesterday", "09:15:00", "good", 1.0, "vote"),
        ("yesterday", "09:16:20", "defective", 1.0, "vote"),
        ("yesterday", "09:18:05", "good", 1.0, "vote"),
        ("yesterday", "09:20:40", "good", 0.87, "vote"),
        ("yesterday", "09:22:10", "defective", 1.0, "vote"),
        ("yesterday", "09:25:00", "good", 1.0, "vote"),
        ("yesterday", "10:40:00", "defective", 0.53, "unsure"),
        ("yesterday", "10:42:30", "good", 1.0, "vote"),
        ("yesterday", "10:45:15", "good", 1.0, "vote"),
        ("yesterday", "10:47:00", "defective", 0.93, "vote"),
        ("today", "08:30:00", "good", 1.0, "vote"),
        ("today", "08:31:40", "good", 1.0, "vote"),
        ("today", "08:33:20", "defective", 1.0, "vote"),
    ]
    return [(f"{day[d].isoformat()}T{t}", decision, confidence, reason) for d, t, decision, confidence, reason in caps]


NOT_COVERED = ["not", "no information", "don't", "doesn't", "cannot", "can't", "unable"]  # ways of saying "I don't know"
REFUSAL = ["only help", "can only", "can't", "cannot", "unable", "not able"]  # ways of politely refusing

CASES = [
    # --- the inspection log (answers come from the tools) ---
    {"category": "log", "question": "How many caps have been inspected in total so far?", "must_include_numbers": [18]},
    {"category": "log", "question": "How many defective caps have there been in total?", "must_include_numbers": [6]},
    {"category": "log", "question": "How many caps were inspected yesterday?", "must_include_numbers": [10]},
    {"category": "log", "question": "What was the defect rate yesterday?", "must_include_numbers": [40]},
    {"category": "log", "question": "How many caps were rejected as unsure yesterday?", "must_include_numbers": [1]},
    {"category": "log", "question": "When did inspections start yesterday?", "must_include": ["9:15"]},
    {"category": "log", "question": "When was the last cap inspected yesterday?", "must_include": ["10:47"]},
    {"category": "log", "question": "How many caps were inspected today?", "must_include_numbers": [3]},
    {"category": "log", "question": "What was the defect rate three days ago?", "must_include_numbers": [20]},
    {"category": "log", "question": "Which caps were defective yesterday, and at what time?",
     "must_include": ["9:16", "9:22", "10:40", "10:47"]},
    {"category": "log", "question": "When exactly were the caps tested yesterday?",  # Faycal's question
     "must_include": ["9:15", "10:47"]},
    {"category": "log", "question": "How many caps were inspected yesterday between 9:00 and 10:00?",
     "must_include_numbers": [6]},
    # --- the inspection documents (answers must cite the right section) ---
    {"category": "documents", "question": "Is the dot in the centre of a cap a defect?",
     "must_include_one_of": ["normal", "not a defect"], "must_cite_one_of": ["Defect definitions > Good cap"]},
    {"category": "documents", "question": "Are faint scratches from handling acceptable?",
     "must_include_one_of": ["acceptable"], "must_cite_one_of": ["Defect definitions > Scratches"]},
    {"category": "documents", "question": "Is a cap with a small hole defective?",
     "must_include": ["defective"], "must_cite_one_of": ["Defect definitions > Holes, cracks and cuts"]},
    {"category": "documents", "question": "What should I do when the screen says unsure?",
     "must_include_one_of": ["by hand", "by eye", "aside"], "must_cite_one_of": ["Inspection procedure > Unsure rejects"]},
    {"category": "documents", "question": "Why is the defect threshold 0.4 and not 0.5?",
     "must_include_one_of": ["missed", "false alarm", "cautious"], "must_cite_one_of": ["Tuning notes > The defect threshold"]},
    {"category": "documents", "question": "How accurate is the model on photos it has never seen?",
     "must_include_numbers": [96.9], "must_cite_one_of": ["Tuning notes > Test results"]},
    {"category": "documents", "question": "Can the station detect a broken tamper ring?",
     "must_include_one_of": ["cannot", "can't", "not"],
     "must_cite_one_of": ["Known limitations > Only what is visible from above", "Defect definitions > What the station looks at"]},
    {"category": "documents", "question": "How do I stop the station?",
     "must_include_one_of": ["press q", "**q**", "'q'", '"q"', "q key"],
     "must_cite_one_of": ["Inspection procedure > Stopping the station"]},
    {"category": "documents", "question": "How many frames must agree before a cap is decided?",
     "must_include_numbers": [12], "must_cite_one_of": ["Tuning notes > Deciding once per cap"]},
    {"category": "documents", "question": "Can I use this station in a real factory?",
     "must_include_one_of": ["not", "learning"], "must_cite_one_of": ["Known limitations > A learning project, not a product"]},
    # --- about the station, but NOT answered by the documents: the assistant must say so ---
    {"category": "not covered", "question": "How much does the inspection station cost?", "must_include_one_of": NOT_COVERED},
    {"category": "not covered", "question": "How many caps per minute can the station inspect?", "must_include_one_of": NOT_COVERED},
    {"category": "not covered", "question": "Who manufactures the bottle caps?", "must_include_one_of": NOT_COVERED},
    {"category": "not covered", "question": "What is the warranty on the station?", "must_include_one_of": NOT_COVERED},
    # --- off-topic: the assistant must politely refuse ---
    {"category": "off-topic", "question": "What is the capital of France?", "must_include_one_of": REFUSAL},
    {"category": "off-topic", "question": "Write me a short poem about cats.", "must_include_one_of": REFUSAL},
    {"category": "off-topic", "question": "How do I cook pasta?", "must_include_one_of": REFUSAL},
    # --- mixed: one question needing both the log and the documents ---
    {"category": "mixed", "question": "What was the defect rate yesterday, and what counts as a scratch defect?",
     "must_include_numbers": [40], "must_cite_one_of": ["Defect definitions > Scratches"]},
    {"category": "mixed", "question": "How many caps were inspected today, and what should I do with an unsure reject?",
     "must_include_numbers": [3], "must_cite_one_of": ["Inspection procedure > Unsure rejects"]},
]
