import fitz  # PyMuPDF


def extract_pages(pdf_bytes: bytes) -> list[dict]:
    """
    Extracts text from a PDF and returns a list of pages with page numbers.

    Output format:
    [
      {"page_num": 1, "text": "...."},
      {"page_num": 2, "text": "...."},
      ...
    ]
    """
    if not pdf_bytes:
        return []

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    pages: list[dict] = []
    for i in range(len(doc)):
        page = doc[i]
        text = page.get_text("text") or ""
        pages.append(
            {
                "page_num": i + 1,     # 1-indexed for user-friendly citations
                "text": text.strip()
            }
        )

    return pages

