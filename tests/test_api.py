"""Tests for src/api.py: the web interface, called like a real program would, but without a server.

TestClient sends HTTP requests straight to the app. The log endpoints read the small sample log
from conftest.py. /ask isn't tested here: it needs Ollama, which GitHub's servers don't have.
"""
from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_health_says_ok():
    response = client.get("/health")
    assert response.status_code == 200  # 200 = "OK, here is your answer"
    assert response.json() == {"status": "ok"}


def test_summary_of_one_day(sample_log):
    response = client.get("/summary", params={"start": "2026-09-26T00:00:00", "end": "2026-09-27T00:00:00"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["defect_rate_percent"] == 66.7
def test_summary_with_a_malformed_date_is_a_bad_request(sample_log):
    response = client.get("/summary", params={"start": "yesterday", "end": "2026-09-27T00:00:00"})
    assert response.status_code == 400
def test_caps_respects_the_limit(sample_log):
    response = client.get("/caps", params={"start": "2026-09-26T00:00:00", "end": "2026-09-27T00:00:00", "limit": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["caps_in_period"] == 3
    assert data["caps_listed"] == 2
def test_summary_without_dates_is_refused():
    response = client.get("/summary")
    assert response.status_code == 422
