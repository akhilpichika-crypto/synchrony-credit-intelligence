import io
from pypdf import PdfReader
from backend.app.database import SessionLocal
from backend.app.models.document_chunk import DocumentChunk
from backend.app.services.embedding_service import chunk_text, generate_embedding


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

def index_document(document_name: str, text: str):
    """
    Split document text into chunks, generate embeddings,
    and store them in PostgreSQL with pgvector.
    """

    chunks = chunk_text(text)

    if not chunks:
        raise ValueError("No text chunks could be generated")

    db = SessionLocal()

    try:
        # Prevent duplicate chunks if the same document is uploaded again
        db.query(DocumentChunk).filter(
            DocumentChunk.document_name == document_name
        ).delete()

        for index, chunk in enumerate(chunks):
            embedding = generate_embedding(chunk)

            document_chunk = DocumentChunk(
                document_name=document_name,
                chunk_index=index,
                content=chunk,
                embedding=embedding
            )

            db.add(document_chunk)

        db.commit()

        return {
            "document_name": document_name,
            "chunks_stored": len(chunks)
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

def retrieve_relevant_chunks(query: str, top_k: int = 3):
    """
    Retrieve the document chunks most semantically similar
    to the user's query.
    """

    query_embedding = generate_embedding(query)

    db = SessionLocal()

    try:
        results = (
            db.query(DocumentChunk)
            .order_by(
                DocumentChunk.embedding.cosine_distance(query_embedding)
            )
            .limit(top_k)
            .all()
        )

        return [
            {
                "document_name": result.document_name,
                "chunk_index": result.chunk_index,
                "content": result.content
            }
            for result in results
        ]

    finally:
        db.close()        