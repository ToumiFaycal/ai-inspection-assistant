"""Shared test setup. pytest loads this file automatically before running the tests."""
import pytest

import assistant_tools
from inspection_log import open_log

# A small, known inspection log: (timestamp, decision, confidence, reason).
SAMPLE_ROWS = [
    ("2026-09-26T16:53:58", "defective", 1.0, "vote"),
    ("2026-09-26T16:54:11", "defective", 1.0, "vote"),
    ("2026-09-26T16:55:16", "good", 1.0, "vote"),
    ("2026-09-27T09:00:00", "good", 0.93, "vote"),
    ("2026-09-27T09:01:00", "defective", 0.47, "unsure"),
]


@pytest.fixture
def sample_log(tmp_path, monkeypatch):
    """A temporary inspection log holding SAMPLE_ROWS, used by the tools instead of the real one.

    Any test that lists `sample_log` as an argument gets this set up before it runs,
    and cleaned up after: the real data/inspections.db is never touched.
    """
    db_path = tmp_path / "test_inspections.db"  # tmp_path: a fresh empty folder for this test
    connection = open_log(db_path)  # creates the table, with your CREATE TABLE
    connection.executemany(
        "INSERT INTO inspections (timestamp, decision, confidence, reason) VALUES (?, ?, ?, ?)",
        SAMPLE_ROWS,
    )
    connection.commit()
    connection.close()
    monkeypatch.setattr(assistant_tools, "DB_PATH", db_path)  # the tools now read this file
    return db_path
