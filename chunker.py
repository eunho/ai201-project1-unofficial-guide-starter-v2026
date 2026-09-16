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

from dataclasses import dataclass

import config
from ingest import Document


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


import re


def split_documents(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    Split documents into chunks based on paragraph and sentence structure.

    Tuned for campus_life (~317 characters/post):
    - Respects natural paragraph breaks (\n\n) and sentence boundaries.
    - Preserves document title on split chunks so each chunk is self-contained.
    - Prevents arbitrary character slicing mid-word or mid-sentence.
    - Avoids creating fragments.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    chunks: list[Chunk] = []

    for doc in documents:
        text = doc.text.strip()
        if not text:
            continue

        lines = [l.strip() for l in text.splitlines() if l.strip()]
        title = lines[0] if lines else ""

        # For documents within chunk_size, keep as a single intact chunk
        if len(text) <= chunk_size:
            chunks.append(
                Chunk(
                    text=text,
                    source=doc.source,
                    index=0,
                    produced_by="chunker.py::split_documents",
                )
            )
            continue

        # Split into paragraph sections
        raw_paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        paras = raw_paras[1:] if (len(raw_paras) > 1 and raw_paras[0] == title) else raw_paras

        # Break any individual paragraph larger than chunk_size into sentence units
        units: list[str] = []
        for p in paras:
            if len(p) > chunk_size:
                sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", p) if s.strip()]
                units.extend(sentences)
            else:
                units.append(p)

        doc_chunks: list[str] = []
        current_parts: list[str] = []
        current_len = 0

        for unit in units:
            unit_len = len(unit)
            title_header = f"{title}\n\n" if title and not unit.startswith(title) else ""
            needed = unit_len + (2 if current_parts else len(title_header))

            if current_parts and (current_len + needed > chunk_size):
                chunk_body = "\n\n".join(current_parts)
                final_text = f"{title}\n\n{chunk_body}" if title and not chunk_body.startswith(title) else chunk_body
                doc_chunks.append(final_text.strip())

                # Overlap: keep last unit if within overlap budget
                last_unit = current_parts[-1]
                if len(last_unit) <= overlap:
                    current_parts = [last_unit, unit]
                    current_len = len(last_unit) + 2 + unit_len
                else:
                    current_parts = [unit]
                    current_len = unit_len
            else:
                current_parts.append(unit)
                current_len += unit_len + (2 if len(current_parts) > 1 else 0)

        if current_parts:
            chunk_body = "\n\n".join(current_parts)
            final_text = f"{title}\n\n{chunk_body}" if title and not chunk_body.startswith(title) else chunk_body
            doc_chunks.append(final_text.strip())

        for idx, c_text in enumerate(doc_chunks):
            chunks.append(
                Chunk(
                    text=c_text,
                    source=doc.source,
                    index=idx,
                    produced_by="chunker.py::split_documents",
                )
            )

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
