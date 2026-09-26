"""Save every cap decision in a small database, so it can be checked and questioned later.

The database is a single file, data/inspections.db, using SQLite (built into Python,
nothing to install). It has one table, "inspections", with one row per cap:

    id          1, 2, 3, ...            numbered automatically
    timestamp   "2026-09-26T14:03:12"   when the decision was made
    decision    "good" or "defective"
    confidence  0.0 to 1.0              share of the voting frames that agreed
    reason      "vote" or "unsure"      how the decision was made

Run this file on its own to see what has been logged so far:
    python src/inspection_log.py
"""
import sqlite3
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "inspections.db"


def open_log(db_path=DB_PATH):
    """Open the database (creating the file if needed), make sure the table exists,
    and return the connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute(
        """CREATE TABLE IF NOT EXISTS inspections (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            decision TEXT NOT NULL,
            confidence REAL NOT NULL,
            reason TEXT NOT NULL
        )"""
    )
    return connection   


def log_decision(connection, decision, confidence, reason):
    """Save one cap decision as a new row, stamped with the current time."""
    timestamp = datetime.now().isoformat(timespec="seconds")  # e.g. "2026-09-26T14:03:12"
    connection.execute(
        "INSERT INTO inspections (timestamp, decision, confidence, reason) VALUES (?, ?, ?, ?)",
        (timestamp, decision, confidence, reason),
    )
    connection.commit()


def recent_decisions(connection, limit=10):
    """Return the last `limit` rows, newest first, as (id, timestamp, decision, confidence, reason)."""
    return connection.execute(
        "SELECT id, timestamp, decision, confidence, reason FROM inspections ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()


def count_by_decision(connection):
    """Return how many caps got each decision, e.g. {"good": 12, "defective": 5}."""
    rows = connection.execute("SELECT decision, COUNT(*) FROM inspections GROUP BY decision").fetchall()
    return dict(rows)


def main():
    connection = open_log()
    print(f"Database: {DB_PATH}")
    print(f"Caps per decision: {count_by_decision(connection)}")
    print("\nLast 10 caps (newest first):")
    for row_id, timestamp, decision, confidence, reason in recent_decisions(connection):
        print(f"  #{row_id:<4} {timestamp}  {decision:9}  confidence {confidence:.2f}  ({reason})")
    connection.close()


if __name__ == "__main__":
    main()
