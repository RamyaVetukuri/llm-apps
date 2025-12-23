from __future__ import annotations


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 1200,
    overlap: int = 200,
    min_chunk_len: int = 200,
) -> list[dict]:
    """
    Convert per-page text into smaller overlapping chunks while preserving page numbers.

    Input format (from pdf_utils.extract_pages):
    [
      {"page_num": 1, "text": "..."},
      {"page_num": 2, "text": "..."},
    ]

    Output format:
    [
      {
        "chunk_id": "c0",
        "text": "...",
        "page_start": 1,
        "page_end": 1
      },
      ...
    ]
    """
    chunks: list[dict] = []
    chunk_id = 0

    # Guardrails
    chunk_size = max(200, chunk_size)
    overlap = max(0, min(overlap, chunk_size - 50))

    for p in pages:
        page_num = p.get("page_num")
        text = (p.get("text") or "").strip()

        # Skip empty pages
        if not text:
            continue

        start = 0
        n = len(text)

        while start < n:
            end = min(start + chunk_size, n)
            chunk_text = text[start:end].strip()

            # Skip tiny chunks (usually noise)
            if len(chunk_text) >= min_chunk_len:
                chunks.append(
                    {
                        "chunk_id": f"c{chunk_id}",
                        "text": chunk_text,
                        "page_start": page_num,
                        "page_end": page_num,
                    }
                )
                chunk_id += 1

            # Move window forward with overlap
            if end == n:
                break
            start = end - overlap

    return chunks
