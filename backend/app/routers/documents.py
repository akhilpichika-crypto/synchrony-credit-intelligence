from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.services.document_service import extract_pdf_text


router = APIRouter(
    prefix="/documents",
    tags=["Supporting Documents"]
)


@router.post("/extract")
async def extract_document(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF documents are supported"
        )

    try:
        contents = await file.read()

        result = extract_pdf_text(contents)

        return {
            "filename": file.filename,
            "status": "processed",
            "page_count": result["page_count"],
            "character_count": result["character_count"],
            "text_preview": result["full_text"][:1000]
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )