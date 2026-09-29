"""Tests for the checks in src/assistant.py that decide whether an answer's citations are real.

These don't need Ollama either: they test plain Python functions on made-up text.
"""
from assistant import find_citations, returned_sources, unverified_citations


def test_find_citations_returns_what_is_inside_the_brackets():
    answer = "Faint scuffs are fine [Defect definitions > Scratches]. Press q [Inspection procedure > Stopping the station]."
    assert find_citations(answer) == ["Defect definitions > Scratches", "Inspection procedure > Stopping the station"]


def test_answer_without_citations_has_none():
    assert find_citations("The defect rate yesterday was 66.7%.") == []


def test_unverified_citations_keeps_only_the_unknown_ones():
    citations = ["Defect definitions > Scratches", "Defect definitions > Storage"]
    sources = {"Defect definitions > Scratches"}
    assert unverified_citations(citations, sources) == ["Defect definitions > Storage"]


def test_every_citation_is_verified_when_all_were_returned():
    citations = ["Defect definitions > Scratches", "Defect definitions > Storage"]
    sources = {"Defect definitions > Scratches", "Defect definitions > Storage"}
    assert unverified_citations(citations, sources) == []


def test_returned_sources_only_comes_from_document_searches():
    tool_log = [
        ("count_decisions", {"total": 6, "good": 2, "defective": 4}),
        ("search_documents", {"found": True, "sections": [
            {"source": "Defect definitions > Good cap", "text": "..."}]}),
        ("search_documents", {"found": False, "message": "Nothing ..."}),
    ]
    assert returned_sources(tool_log) == {"Defect definitions > Good cap"}
