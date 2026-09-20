import io
from pypdf import PdfReader


def extract_pdf_text(file_bytes: bytes):
    """
    Extract text from a text-based PDF.
    This prototype does not perform OCR on scanned PDFs.
    """

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except Exception:
        raise ValueError("Unable to read the PDF document")

    if len(reader.pages) == 0:
        raise ValueError("PDF contains no pages")

    extracted_pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            extracted_pages.append({
                "page": page_number,
                "text": text.strip()
            })

    if not extracted_pages:
        raise ValueError(
            "No extractable text found. Scanned PDFs are not supported "
            "in this prototype."
        )

    full_text = "\n\n".join(
        page["text"] for page in extracted_pages
    )

    return {
        "pages": extracted_pages,
        "full_text": full_text,
        "page_count": len(reader.pages),
        "character_count": len(full_text)
    }