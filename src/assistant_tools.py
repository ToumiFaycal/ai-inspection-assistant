"""Tools the assistant can call: small, read-only questions to the inspection log.

The language model never reads the database itself. It asks for one of these functions
by name, assistant.py runs it and hands the result back. So every number in an answer
comes from here, not from the model's memory.

Each tool:
  - has a docstring the model reads to decide when to use it, so keep it clear and precise,
  - opens the log read-only, so the assistant can never change or delete anything,
  - returns plain data (numbers, text, lists, dicts).
"""
import sqlite3

from inspection_log import DB_PATH, count_by_decision


def read_only_connection():
    """Open the inspection log so it can be read but never changed."""
    return sqlite3.connect(DB_PATH.as_uri() + "?mode=ro", uri=True)


def count_decisions() -> dict:
    """Count every cap in the inspection log since it started (all days together):
    how many were inspected in total, how many were good and how many defective.

    Returns:
      dict: {"total": number of caps, "good": number of good caps, "defective": number of defective caps}
    """
    connection = read_only_connection()
    counts = count_by_decision(connection)
    connection.close()
    return {
        "total": counts.get("good", 0) + counts.get("defective", 0),
        "good": counts.get("good", 0),
        "defective": counts.get("defective", 0)
    }
    pass


# The tools the assistant is allowed to use. Add each new tool function here.
TOOLS = [count_decisions]
