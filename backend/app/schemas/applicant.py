from pydantic import BaseModel, Field


class ApplicantInput(BaseModel):
    checking_status: str
    duration_months: int = Field(gt=0, le=120)
    credit_history: str
    purpose: str
    credit_amount: float = Field(gt=0)
    savings_status: str
    employment_status: str
    installment_rate: int = Field(ge=1, le=4)
    personal_status: str
    other_debtors: str
    residence_duration: int = Field(ge=1, le=4)
    property: str
    age: int = Field(ge=18, le=100)
    other_installment_plans: str
    housing: str
    existing_credits: int = Field(ge=1)
    job: str
    dependents: int = Field(ge=1)
    telephone: str
    foreign_worker: str