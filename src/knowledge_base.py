"""The inspection documents, made searchable for the assistant (retrieval-augmented generation).

Step 1: split every document in knowledge/ into its sections, each labelled with where
it comes from, so that the assistant's answers can cite their source:

    {"source": "Defect definitions > Scratches",
     "text": "A cap is defective when its top face has clear scratches, or many scratches. ..."}

Step 2: turn text into embeddings, lists of 768 numbers that capture its meaning, using a
small local model (embeddinggemma in Ollama). Texts with similar meanings get similar
numbers, and cosine similarity measures how close two of them are.

Run this file on its own to see the sections and a few similarity scores:
    python src/knowledge_base.py
"""
from collections import Counter
from pathlib import Path

import numpy as np
import ollama

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
EMBED_MODEL = "embeddinggemma"  # a small model that only turns text into numbers (it can't chat)


def make_section(title, heading, lines):
    """Build one section: {"source": "<title> > <heading>", "text": "<its lines, joined>"}."""
    return {"source": f"{title} > {heading}", "text": "\n".join(lines).strip()}


def split_into_sections(path):
    """Split one Markdown document into its "## " sections.

    Returns a list of dicts: {"source": "<document title> > <section heading>", "text": "<section text>"}.
    The document title is the text of its "# " line. The short introduction between the title
    and the first "## " heading doesn't belong to any section and is left out.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = ""
    heading = ""  # stays "" (which counts as false) until the first "## " heading
    its_lines = []
    results = []
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("## "):
            if heading and its_lines:  # false for the introduction: it's dropped, not saved
                results.append(make_section(title, heading, its_lines))
            heading = line[3:].strip()
            its_lines = []
        else:
            its_lines.append(line)
    # Add the last section: no "## " comes after it to trigger the save above
    if heading and its_lines:
        results.append(make_section(title, heading, its_lines))
    return results


def load_sections():
    """Split every document in knowledge/ and return all their sections in one list."""
    sections = []
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        sections.extend(split_into_sections(path) or [])
    return sections


def embed(texts):
    """Turn a list of texts into embeddings: a NumPy array with one row of 768 numbers per text."""
    response = ollama.embed(model=EMBED_MODEL, input=texts)
    return np.array(response.embeddings)


def section_to_embed(section):
    """The text used to embed a section: its source label, then its text.
    Measured on 10 test questions, adding the label found the right section first more often."""
    return f"{section['source']}\n{section['text']}"


def cosine_similarity(a, b):
    """How close two embeddings are in meaning: 1.0 = same direction (same meaning),
    around 0 = unrelated. `a` and `b` are NumPy arrays of the same length."""
    return float((a @ b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main():
    sections = load_sections()
    per_document = Counter(section["source"].split(" > ")[0] for section in sections)
    for title, count in per_document.items():
        print(f"{title}: {count} sections")
    print(f"Total: {len(sections)} sections")

    empty = [section["source"] for section in sections if not section["text"]]
    if empty:
        print(f"Warning, sections with no text: {empty}")
    if sections:
        example = sections[0]
        print(f"\nExample:\n  source: {example['source']}\n  text:   {example['text'][:200]}...")

    print("\nEmbeddings (the first call can take ~15 s while Ollama loads the model):")
    phrases = ["A crushed cap", "A cap with a deformed rim", "The weather is nice today"]
    vectors = embed(phrases)
    print(f"  each text becomes {vectors.shape[1]} numbers, e.g. '{phrases[0]}' starts with {np.round(vectors[0, :5], 3)}")
    for i, j in [(0, 1), (0, 2)]:
        score = cosine_similarity(vectors[i], vectors[j])
        print(f"  '{phrases[i]}' vs '{phrases[j]}': {score}")


if __name__ == "__main__":
    main()
