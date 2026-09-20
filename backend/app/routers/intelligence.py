from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.services.document_service import retrieve_relevant_chunks
from backend.app.services.llm_service import generate_credit_explanation


router = APIRouter(
    prefix="/intelligence",
    tags=["Credit Intelligence"]
)


class ExplanationRequest(BaseModel):
    risk_probability: float
    risk_band: str
    shap_factors: list
    behavioral_data: dict
    query: str = (
        "What evidence describes the applicant's income stability, "
        "financial obligations, payment behavior and cash flow?"
    )


@router.post("/explain")
def generate_explanation(request: ExplanationRequest):
    try:
        evidence = retrieve_relevant_chunks(
            query=request.query,
            top_k=3
        )

        explanation = generate_credit_explanation(
            risk_probability=request.risk_probability,
            risk_band=request.risk_band,
            shap_factors=request.shap_factors,
            behavioral_data=request.behavioral_data,
            retrieved_evidence=evidence
        )

        return {
            "risk_probability": request.risk_probability,
            "risk_band": request.risk_band,
            "retrieved_evidence": evidence,
            "explanation": explanation
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate explanation: {str(error)}"
        )