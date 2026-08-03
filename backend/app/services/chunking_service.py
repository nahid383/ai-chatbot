"""
Recursive, structure-aware chunking (Lesson 3, Strategy 2).

We try to split on the "biggest" natural boundary first (paragraphs),
and only fall back to smaller boundaries (sentences, then words) if a
piece is still too large. This keeps chunks semantically coherent
instead of cutting mid-sentence.
"""

from app.config import settings

SEPARATORS = ["\n\n", "\n", ". ", " "]


def _split_on_separator(text: str, separator: str) -> list[str]:
    if separator == "":
        return list(text)
    return text.split(separator)


def _recursive_split(text: str, separators: list[str], chunk_size: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    if not separators:
        # Last resort: hard cut at chunk_size.
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    separator, *remaining_separators = separators
    pieces = _split_on_separator(text, separator)

    chunks: list[str] = []
    current = ""
    for piece in pieces:
        candidate = (current + separator + piece) if current else piece
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            if len(piece) > chunk_size:
                # This single piece is still too big - recurse with a
                # smaller separator (e.g. split this paragraph by sentence).
                chunks.extend(_recursive_split(piece, remaining_separators, chunk_size))
                current = ""
            else:
                current = piece
    if current:
        chunks.append(current)
    return chunks


def _add_overlap(chunks: list[str], overlap: int) -> list[str]:
    if overlap <= 0 or len(chunks) <= 1:
        return chunks
    overlapped = [chunks[0]]
    for i in range(1, len(chunks)):
        prev_tail = chunks[i - 1][-overlap:]
        overlapped.append(prev_tail + " " + chunks[i])
    return overlapped


def chunk_text(
    text: str,
    chunk_size: int = settings.CHUNK_SIZE,
    overlap: int = settings.CHUNK_OVERLAP,
) -> list[str]:
    """
    Public entry point. Cleans whitespace, then recursively splits,
    then adds overlap between consecutive chunks.
    """
    cleaned = " ".join(text.split())  # collapse repeated whitespace/newlines
    # Preserve paragraph breaks for the splitter to use as boundaries -
    # we only collapsed *within* lines above via split()/join(), so
    # re-fetch structure from the original text's blank lines instead:
    cleaned = "\n\n".join(p.strip() for p in text.split("\n\n") if p.strip())

    raw_chunks = _recursive_split(cleaned, SEPARATORS, chunk_size)
    raw_chunks = [c.strip() for c in raw_chunks if c.strip()]
    return _add_overlap(raw_chunks, overlap)
