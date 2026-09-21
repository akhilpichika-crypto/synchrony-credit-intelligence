import logging
import pandas as pd

from backend.app.services.explanation_service import explain_prediction


logger = logging.getLogger("credit_intelligence")


def predict_risk(model, applicant_data: dict):

    annual_income = float(applicant_data["annual_income"])
    requested_amount = float(
        applicant_data["requested_loan_amount"]
    )

    # Build exactly the 8 features used during training
    model_input = {
        "customer_age": int(applicant_data["age"]),
        "customer_income_inr": annual_income,
        "home_ownership": applicant_data["home_ownership"],
        "employment_duration": float(
            applicant_data["employment_duration"]
        ),
        "loan_intent": applicant_data["loan_intent"],
        "loan_amount_inr": requested_amount,
        "term_years": float(
            applicant_data["duration_months"]
        ) / 12.0,
        "loan_to_income_ratio": (
            requested_amount / annual_income
        ),
    }

    input_df = pd.DataFrame([model_input])

    risk_probability = model.predict_proba(input_df)[0][1]

    if risk_probability < 0.30:
        risk_level = "LOW"
    elif risk_probability < 0.60:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    explanations = explain_prediction(
        model,
        model_input,
        top_n=5
    )

    logger.info(
        "Risk assessment completed | risk_band=%s | model_version=2.0",
        risk_level,
    )

    return {
        "risk_probability": round(float(risk_probability), 4),
        "risk_percentage": round(float(risk_probability) * 100, 2),
        "risk_level": risk_level,
        "model_version": "2.0",
        "top_factors": explanations
    }