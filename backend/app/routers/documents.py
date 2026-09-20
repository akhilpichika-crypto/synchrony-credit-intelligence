from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.services.document_service import (
    extract_pdf_text,
    index_document,
    retrieve_relevant_chunks
)


router = APIRouter(
    prefix="/documents",
    tags=["Supporting Documents"]
)


@router.post("/index")
async def index_pdf_document(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF documents are supported"
        )

    try:
        contents = await file.read()

        extracted = extract_pdf_text(contents)

        indexed = index_document(
            document_name=file.filename,
            text=extracted["full_text"]
        )

        return {
            "filename": file.filename,
            "status": "indexed",
            "page_count": extracted["page_count"],
            "character_count": extracted["character_count"],
            "chunks_stored": indexed["chunks_stored"]
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

@router.get("/search")
def search_documents(query: str, top_k: int = 3):

    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    results = retrieve_relevant_chunks(
        query=query,
        top_k=top_k
    )

    return {
        "query": query,
        "results": results
    }