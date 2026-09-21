from fastapi import APIRouter, HTTPException, Depends
from backend.app.services.auth_service import require_role
from pydantic import BaseModel

from backend.app.services.affordability_service import (
    calculate_affordable_emi,
    calculate_loan_capacity,
    PROTOTYPE_APR_BY_RISK,
)
router = APIRouter(
    prefix="/affordability",
    tags=["Affordability"],
)


class AffordabilityRequest(BaseModel):
    stable_monthly_income: float
    observed_monthly_expenses: float
    city: str
    existing_monthly_obligations: float = 0
    risk_band: str
    duration_months: int


@router.post("/analyze")
def analyze_affordability(
    request: AffordabilityRequest,
    current_user=Depends(
        require_role("ANALYST", "ADMIN")
    ),
):
    try:
        risk_band = request.risk_band.upper()

        if risk_band not in PROTOTYPE_APR_BY_RISK:
            raise ValueError(
                "Risk band must be LOW, MEDIUM or HIGH"
            )

        affordability = calculate_affordable_emi(
            stable_monthly_income=request.stable_monthly_income,
            observed_monthly_expenses=request.observed_monthly_expenses,
            existing_monthly_obligations=request.existing_monthly_obligations,
            city=request.city,
        )

        estimated_apr = PROTOTYPE_APR_BY_RISK[risk_band]

        loan_capacity = calculate_loan_capacity(
            affordable_emi=affordability["affordable_emi"],
            annual_apr=estimated_apr,
            duration_months=request.duration_months,
        )

        return {
            **affordability,
            "risk_band": risk_band,
            "estimated_apr": estimated_apr,
            "duration_months": request.duration_months,
            "indicative_loan_capacity": loan_capacity,
            "pricing_basis": (
                "Illustrative prototype APR based on model risk band"
            ),
            "disclaimer": (
                "Prototype affordability estimate only. "
                "Not a lending offer, approval, or actual lender pricing."
            ),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )