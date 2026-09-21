from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.services.document_service import (
    extract_pdf_text,
    index_document,
    retrieve_relevant_chunks,
)


MAX_PDF_SIZE = 5 * 1024 * 1024  # 5 MB


router = APIRouter(
    prefix="/documents",
    tags=["Supporting Documents"],
)


@router.post("/index")
async def index_pdf_document(file: UploadFile = File(...)):

    # 1. Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A PDF document is required.",
        )

    # 2. Validate file extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF documents are supported.",
        )

    # 3. Validate MIME type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file type.",
        )

    # 4. Read uploaded file
    contents = await file.read()

    # 5. Reject empty files
    if len(contents) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty.",
        )

    # 6. Limit upload size
    if len(contents) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF exceeds the 5 MB size limit.",
        )

    # 7. Check actual PDF file signature
    if not contents.startswith(b"%PDF"):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid PDF.",
        )

    try:
        # Extract text from PDF
        extracted = extract_pdf_text(contents)

        # Chunk, embed and store in pgvector
        indexed = index_document(
            document_name=file.filename,
            text=extracted["full_text"],
        )

        return {
            "filename": file.filename,
            "status": "indexed",
            "page_count": extracted["page_count"],
            "character_count": extracted["character_count"],
            "chunks_stored": indexed["chunks_stored"],
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:
        # Do not expose internal database/library errors
        raise HTTPException(
            status_code=500,
            detail="Unable to process supporting document.",
        )


@router.get("/search")
def search_documents(
    query: str,
    document_name: str,
    top_k: int = 3,
):

    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    if not document_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Document name cannot be empty.",
        )

    if top_k < 1 or top_k > 10:
        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 10.",
        )

    try:
        results = retrieve_relevant_chunks(
            query=query,
            document_name=document_name,
            top_k=top_k,
        )

        return {
            "query": query,
            "document_name": document_name,
            "results": results,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to search supporting documents.",
        )