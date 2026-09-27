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
from datetime import datetime

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


def current_time() -> dict:
    """Get the current date and time of the inspection station. Call this first whenever a
    question mentions "today", "yesterday", "now", "this morning", "the last hour" or any
    other period relative to the present.

    Returns:
      dict: {"now": "YYYY-MM-DDTHH:MM:SS", "today": "YYYY-MM-DD", "weekday": day name, e.g. "Sunday"}
    """
    now = datetime.now()
    return {"now": now.isoformat(timespec="seconds"), "today": now.date().isoformat(), "weekday": now.strftime("%A")}


def summary_between(start: str, end: str) -> dict:
    """Summarise the caps inspected during a period of time: how many in total, how many good
    and defective, how many were rejected because the machine was unsure, and the defect rate
    in percent. Use it for any question about a period ("today", "yesterday", "this morning",
    "the last hour", "between 10:00 and 11:00"...). Call current_time first to know what
    "today" or "now" is.

    Args:
      start (str): start of the period (included), as "YYYY-MM-DDTHH:MM:SS", e.g. "2026-09-26T08:00:00"
      end (str): end of the period (not included), same format, e.g. "2026-09-26T12:00:00"

    Returns:
      dict: {"period_start": the start you asked about, "period_end": the end you asked about,
             "first_inspection": time of the first cap actually inspected in the period,
             "last_inspection": time of the last cap actually inspected in the period
             (both None when no caps were inspected), "total": ..., "good": ..., "defective": ...,
             "unsure_rejects": ..., "defect_rate_percent": ... (None when no caps were inspected)}
    """
    connection = read_only_connection()
    try:
        # Check that start and end are valid dates
        datetime.fromisoformat(start)
        datetime.fromisoformat(end)

        # Count the caps in the period
        cursor = connection.execute(
            "SELECT decision, COUNT(*) FROM inspections WHERE timestamp >= ? AND timestamp < ? GROUP BY decision",
            (start, end)
        )
        counts = dict(cursor.fetchall())

        # Count the unsure rejects in the period
        cursor = connection.execute(
            "SELECT COUNT(*) FROM inspections WHERE timestamp >= ? AND timestamp < ? AND reason = 'unsure'",
            (start, end)
        )
        unsure_rejects = cursor.fetchone()[0]

        first_inspection, last_inspection = connection.execute(
            "SELECT MIN(timestamp), MAX(timestamp) FROM inspections WHERE timestamp >= ? AND timestamp < ?",
            (start, end)
        ).fetchone()

        # Calculate the defect rate
        total = counts.get("good", 0) + counts.get("defective", 0)
        defect_rate_percent = round(100 * counts.get("defective", 0) / total, 1) if total > 0 else None

        return {
            "period_start": start,
            "period_end": end,
            "first_inspection": first_inspection,
            "last_inspection": last_inspection,
            "total": total,
            "good": counts.get("good", 0),
            "defective": counts.get("defective", 0),
            "unsure_rejects": unsure_rejects,
            "defect_rate_percent": defect_rate_percent
        }
    finally:
        connection.close()


def list_caps_between(start: str, end: str, limit: int = 20) -> dict:
    """List the individual caps inspected during a period of time, oldest first: the exact time
    of each inspection, its decision, confidence and reason. Use it for questions about exact
    times ("when exactly were the caps tested?") or about specific caps ("which caps were
    defective yesterday?", "show me the unsure rejects"). Call current_time first when the
    question mentions "today", "yesterday", "now" or another period relative to the present.

    Args:
      start (str): start of the period (included), as "YYYY-MM-DDTHH:MM:SS", e.g. "2026-09-26T08:00:00"
      end (str): end of the period (not included), same format, e.g. "2026-09-27T00:00:00"
      limit (int): the most caps to list, 20 if not given

    Returns:
      dict: {"period_start": ..., "period_end": ..., "caps_in_period": number of caps in the period,
             "caps_listed": how many are listed below (fewer than caps_in_period when limited),
             "caps": [{"time": ..., "decision": ..., "confidence": ..., "reason": ...}, ...]}
    """
    
    connection = read_only_connection()
    try:
        # Check that start and end are valid dates
        datetime.fromisoformat(start)
        datetime.fromisoformat(end)

        limit = int(limit)

        # Count the caps in the period
        cursor = connection.execute(
            "SELECT COUNT(*) FROM inspections WHERE timestamp >= ? AND timestamp < ?",
            (start, end)
        )
        caps_in_period = cursor.fetchone()[0]

        # Get the rows themselves
        cursor = connection.execute(
            "SELECT timestamp, decision, confidence, reason FROM inspections "
            "WHERE timestamp >= ? AND timestamp < ? ORDER BY timestamp LIMIT ?",
            (start, end, limit)
        )
        rows = cursor.fetchall()

        caps_listed = len(rows)
        caps = [{"time": t, "decision": d, "confidence": round(c, 2), "reason": r} for t, d, c, r in rows]

        return {
            "period_start": start,
            "period_end": end,
            "caps_in_period": caps_in_period,
            "caps_listed": caps_listed,
            "caps": caps
        }
    finally:
        connection.close()

# The tools the assistant is allowed to use. Add each new tool function here.
TOOLS = [count_decisions, current_time, summary_between, list_caps_between]
