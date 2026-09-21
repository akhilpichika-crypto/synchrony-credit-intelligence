from typing import Any
import time
from fastapi import APIRouter, HTTPException, Depends
from backend.app.services.auth_service import require_role
from pydantic import BaseModel, Field

from backend.app.services.document_service import retrieve_relevant_chunks
from backend.app.services.llm_service import generate_credit_explanation


router = APIRouter(
    prefix="/intelligence",
    tags=["Credit Intelligence"],
)


class ShapFactor(BaseModel):
    feature: str
    shap_value: float


class ExplanationRequest(BaseModel):
    risk_probability: float = Field(
        ge=0.0,
        le=1.0,
    )

    risk_band: str

    shap_factors: list[ShapFactor]

    behavioral_data: dict[str, Any]

    document_name: str = Field(
        min_length=1,
        max_length=255,
    )

    query: str = Field(
        default=(
            "What evidence describes the applicant's income stability, "
            "financial obligations, payment behavior and cash flow?"
        ),
        min_length=1,
        max_length=500,
    )


@router.post("/explain")
def generate_explanation(
    request: ExplanationRequest,
    current_user=Depends(require_role("ANALYST")),
):

    # Validate risk band explicitly
    risk_band = request.risk_band.upper()

    if risk_band not in {"LOW", "MEDIUM", "HIGH"}:
        raise HTTPException(
            status_code=400,
            detail="Risk band must be LOW, MEDIUM or HIGH.",
        )

    try:
        retrieval_start = time.perf_counter()
        evidence = retrieve_relevant_chunks(
            query=request.query,
            document_name=request.document_name,
            top_k=3,
        )
        retrieval_time = time.perf_counter() - retrieval_start
        print(
                f"[TIMING] Semantic retrieval: "
                f"{retrieval_time:.2f} seconds"
            )

        if not evidence:
            raise HTTPException(
                status_code=404,
                detail=(
                    "No indexed evidence found for "
                    "the selected document."
                ),
            )

        gemini_start = time.perf_counter()

        explanation = generate_credit_explanation(
            risk_probability=request.risk_probability,
            risk_band=risk_band,
            shap_factors=[
                factor.model_dump()
                for factor in request.shap_factors
            ],
            behavioral_data=request.behavioral_data,
            retrieved_evidence=evidence,
        )

        gemini_time = time.perf_counter() - gemini_start

        print(
            f"[TIMING] Gemini generation: "
            f"{gemini_time:.2f} seconds"
        )

        print(
            f"[TIMING] Total AI pipeline: "
            f"{retrieval_time + gemini_time:.2f} seconds"
        )

        return {
            "risk_probability": request.risk_probability,
            "risk_band": risk_band,
            "document_name": request.document_name,
            "retrieved_evidence": evidence,
            "explanation": explanation,
        }

    except HTTPException:
        # Preserve intentional 4xx errors.
        raise

    except Exception as error:
        print("Credit intelligence explanation error:", repr(error))

        error_text = str(error).lower()

        if "429" in error_text or "rate limit" in error_text:
            raise HTTPException(
                status_code=429,
                detail=(
                    "AI explanation service is temporarily rate-limited. "
                    "Please try again shortly."
                ),
            )

        raise HTTPException(
            status_code=500,
            detail="Unable to generate credit intelligence explanation."
        )