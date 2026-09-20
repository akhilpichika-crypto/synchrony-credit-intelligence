import pandas as pd

from backend.app.services.explanation_service import explain_prediction


def predict_risk(model, applicant_data: dict):
    input_df = pd.DataFrame([applicant_data])

    risk_probability = model.predict_proba(input_df)[0][1]

    if risk_probability < 0.30:
        risk_level = "LOW"
    elif risk_probability < 0.60:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    explanations = explain_prediction(
        model,
        applicant_data,
        top_n=5
    )

    return {
        "risk_probability": round(float(risk_probability), 4),
        "risk_percentage": round(float(risk_probability) * 100, 2),
        "risk_level": risk_level,
        "model_version": "1.0",
        "top_factors": explanations
    }