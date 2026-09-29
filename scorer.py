"""Judging logic for the Unit 2 evaluation run."""

from __future__ import annotations

import re


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("_", " ").replace("/", " ").replace(".", " ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _contains_all(answer: str, expected: str) -> bool:
    answer_norm = _normalize(answer)
    expected_norm = _normalize(expected)
    if not expected_norm:
        return False
    return expected_norm in answer_norm


def _source_names(results) -> set[str]:
    out: set[str] = set()
    for r in results or []:
        source = getattr(r, "source", None)
        if source:
            out.add(_normalize(str(source)))
    return out


def judge(question: str, expects: str, answer: str, results) -> bool:
    """Return True when an answer is both on-topic and sourced correctly.

    The evaluation rubric in this project expects the answer itself to contain the
    expected fact, and to name at least one retrieved source document.
    """
    if not answer:
        return False

    if not _contains_all(answer, expects):
        return False

    source_names = _source_names(results)
    if not source_names:
        return False

    answer_norm = _normalize(answer)
    return any(src in answer_norm for src in source_names)
