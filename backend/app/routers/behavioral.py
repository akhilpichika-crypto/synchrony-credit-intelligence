from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from backend.app.services.auth_service import require_role
from backend.app.services.behavioral_service import analyze_transactions


router = APIRouter(
    prefix="/behavior",
    tags=["Behavioral Intelligence"]
)
MAX_CSV_SIZE = 2 * 1024 * 1024  # 2 MB

@router.post("/analyze")
async def analyze_transaction_file(
    file: UploadFile = File(...),
    current_user=Depends(require_role("ANALYST")),
):
    # 1. Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A CSV file is required."
        )

    # 2. Validate extension
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV transaction files are supported."
        )

    # 3. Validate MIME type
    allowed_types = {
        "text/csv",
        "application/csv",
        "application/vnd.ms-excel",
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid CSV file type."
        )

    # 4. Read file
    file_bytes = await file.read()

    # 5. Validate size
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded CSV is empty."
        )

    if len(file_bytes) > MAX_CSV_SIZE:
        raise HTTPException(
            status_code=413,
            detail="CSV file exceeds the 2 MB size limit."
        )

    try:
        return analyze_transactions(file_bytes)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        # Don't expose internal exception details to the client.
        raise HTTPException(
            status_code=500,
            detail="Unable to process transaction file."
        )