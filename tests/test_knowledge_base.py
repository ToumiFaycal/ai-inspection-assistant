"""Tests for src/knowledge_base.py: splitting documents into sections, and cosine similarity.

These don't need Ollama: they test your own code, not the embedding model.
"""
import numpy as np
import pytest

from knowledge_base import cosine_similarity, load_sections, split_into_sections

SAMPLE_DOCUMENT = """# Sample document

A one-line introduction that belongs to no section.

## First section
Line A.

## Second section
Line B.
Line C.
"""


def test_split_labels_each_section_with_title_and_heading(tmp_path):
    path = tmp_path / "sample.md"
    path.write_text(SAMPLE_DOCUMENT, encoding="utf-8")

    sections = split_into_sections(path)

    assert [section["source"] for section in sections] == [
        "Sample document > First section",
        "Sample document > Second section",
    ]


def test_introduction_is_left_out(tmp_path):
    path = tmp_path / "sample.md"
    path.write_text(SAMPLE_DOCUMENT, encoding="utf-8")

    sections = split_into_sections(path)

    assert not any("one-line introduction" in s["text"] for s in sections)
def test_last_section_keeps_all_its_lines(tmp_path):
    path = tmp_path / "sample.md"
    path.write_text(SAMPLE_DOCUMENT, encoding="utf-8")

    sections = split_into_sections(path)

    assert sections[-1]["text"] == "Line B.\nLine C."
def test_every_real_section_has_text():
    sections = load_sections()

    assert all(s["text"] for s in sections)
def test_cosine_similarity_same_direction_is_1():
    assert cosine_similarity(np.array([3.0, 4.0]), np.array([6.0, 8.0])) == pytest.approx(1.0)
def test_cosine_similarity_right_angle_is_0():
    assert cosine_similarity(np.array([1.0, 0.0]), np.array([0.0, 1.0])) == pytest.approx(0.0)
def test_cosine_similarity_opposite_is_minus_1():
    assert cosine_similarity(np.array([1.0, 0.0]), np.array([-1.0, 0.0])) == pytest.approx(-1.0)
