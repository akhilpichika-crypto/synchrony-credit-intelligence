from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.services.behavioral_service import analyze_transactions


router = APIRouter(
    prefix="/behavior",
    tags=["Behavioral Intelligence"]
)


@router.post("/analyze")
async def analyze_behavior(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV transaction files are supported"
        )

    try:
        contents = await file.read()

        result = analyze_transactions(contents)

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )