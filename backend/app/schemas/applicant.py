from pydantic import BaseModel, Field


class ApplicantInput(BaseModel):
    age: int = Field(ge=18, le=100)

    annual_income: float = Field(gt=0)

    requested_loan_amount: float = Field(gt=0)

    home_ownership: str

    employment_duration: float = Field(ge=0)

    loan_intent: str

    duration_months: int = Field(gt=0, le=120)