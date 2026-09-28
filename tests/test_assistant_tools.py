"""Tests for src/assistant_tools.py: the inspection log tools, on a small known log.

Every test here takes the `sample_log` fixture (see conftest.py), so the tools read
SAMPLE_ROWS from a temporary database instead of the real log:
    2026-09-26: 16:53:58 defective, 16:54:11 defective, 16:55:16 good           (all "vote")
    2026-09-27: 09:00:00 good (vote), 09:01:00 defective (unsure)
"""
import pytest

from assistant_tools import count_decisions, list_caps_between, summary_between


def test_count_decisions_counts_every_cap(sample_log):
    assert count_decisions() == {"total": 5, "good": 2, "defective": 3}


def test_summary_of_one_day(sample_log):
    result = summary_between("2026-09-26T00:00:00", "2026-09-27T00:00:00")
    assert result["total"] == 3
    assert result["good"] == 1
    assert result["defective"] == 2
    assert result["unsure_rejects"] == 0
    assert result["defect_rate_percent"] == 66.7
    assert result["first_inspection"] == "2026-09-26T16:53:58"
    assert result["last_inspection"] == "2026-09-26T16:55:16"
def test_summary_counts_unsure_rejects(sample_log):
    result = summary_between("2026-09-27T00:00:00", "2026-09-28T00:00:00")
    assert result["total"] == 2
    assert result["unsure_rejects"] == 1
    assert result["defect_rate_percent"] == 50.0
def test_summary_of_a_period_without_caps(sample_log):
    result = summary_between("2026-09-25T00:00:00", "2026-09-26T00:00:00")
    assert result["total"] == 0
    assert result["defect_rate_percent"] is None
    assert result["first_inspection"] is None
def test_end_of_the_period_is_not_included(sample_log):
    result = summary_between("2026-09-26T16:53:58", "2026-09-26T16:54:11")
    assert result["total"] == 1
def test_list_respects_the_limit(sample_log):
    result = list_caps_between("2026-09-26T00:00:00", "2026-09-27T00:00:00", limit=2)
    assert result["caps_in_period"] == 3
    assert result["caps_listed"] == 2
    assert result["caps"][0]["time"] == "2026-09-26T16:53:58"
    assert result["caps"][1]["time"] == "2026-09-26T16:54:11"
def test_malformed_date_is_refused(sample_log):
    with pytest.raises(ValueError):
        summary_between("yesterday", "2026-09-27T00:00:00")
