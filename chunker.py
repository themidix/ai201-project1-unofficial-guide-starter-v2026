"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document

_HEADING_RE = re.compile(r"^(#{1,6}\s+.*)$", re.MULTILINE)
_SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _sections(text: str) -> list[tuple[str, str]]:
    """
    Split markdown text on its heading lines.

    Returns (heading, body) pairs in document order. Anything before the
    first heading (there usually isn't any) comes back with an empty heading.
    """
    matches = list(_HEADING_RE.finditer(text))
    if not matches:
        return [("", text.strip())]

    sections: list[tuple[str, str]] = []
    if matches[0].start() > 0:
        preamble = text[: matches[0].start()].strip()
        if preamble:
            sections.append(("", preamble))

    for i, match in enumerate(matches):
        heading = match.group(1).strip()
        body_start = match.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append((heading, text[body_start:body_end].strip()))

    return sections


def _paragraphs(body: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def _sentences(paragraph: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_END_RE.split(paragraph) if s.strip()]


def _group(pieces: list[str], limit: int) -> list[str]:
    """
    Greedily join whole pieces (paragraphs, or sentences) up to `limit`
    characters. Never splits a piece itself, so the boundary between groups is
    always a boundary that was already there.
    """
    groups: list[str] = []
    current: list[str] = []
    current_len = 0
    for piece in pieces:
        added_len = len(piece) + (2 if current else 0)
        if current and current_len + added_len > limit:
            groups.append("\n\n".join(current))
            current, current_len, added_len = [], 0, len(piece)
        current.append(piece)
        current_len += added_len
    if current:
        groups.append("\n\n".join(current))
    return groups


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Heading-aware chunking for the city_guides corpus.

    Every guide is a run of `#`/`##` headings — "Getting there", "When to
    go" — and the answer to any question about a town lives entirely inside
    the section its heading introduces. Cutting at a fixed character count
    ignores that: it happily slices a heading away from the paragraph under
    it, or stops mid-sentence (the starter's own sample chunks show the
    accessibility guide's "Practical" section getting cut off after "for
    limited hours").

    So a chunk here never crosses a heading boundary. Each section becomes
    one chunk, with its heading kept at the top. A section longer than
    config.CHUNK_SIZE is split further, but only on paragraph breaks, or on
    sentence boundaries if a single paragraph is still too long — never in
    the middle of a sentence — and every piece gets the heading repeated at
    the top so it still reads, and cites, on its own.
    """
    limit = config.CHUNK_SIZE
    chunks: list[Chunk] = []

    for doc in documents:
        index = 0
        for heading, body in _sections(doc.text):
            if not body:
                continue

            full = f"{heading}\n\n{body}" if heading else body
            if len(full) <= limit:
                pieces = [full]
            else:
                expanded: list[str] = []
                for paragraph in _paragraphs(body):
                    if len(paragraph) <= limit:
                        expanded.append(paragraph)
                    else:
                        expanded.extend(_group(_sentences(paragraph), limit))
                pieces = [
                    f"{heading}\n\n{group}" if heading else group
                    for group in _group(expanded, limit)
                ]

            for piece in pieces:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                index += 1

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
