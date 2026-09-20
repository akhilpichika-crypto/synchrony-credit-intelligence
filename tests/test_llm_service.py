from backend.app.services.llm_service import generate_credit_explanation
from backend.app.services.document_service import retrieve_relevant_chunks


# Known model result from our test applicant
risk_probability = 0.1342
risk_band = "LOW"

# Known SHAP factors
shap_factors = [
    {"feature": "duration_months", "shap_value": -0.1065},
    {"feature": "savings_status", "shap_value": -0.0770},
    {"feature": "credit_history", "shap_value": -0.0762},
    {"feature": "checking_status", "shap_value": 0.0715},
    {"feature": "property", "shap_value": -0.0470},
]

# Behavioral indicators from our synthetic transaction CSV
behavioral_data = {
    "income_stability": 98.76,
    "cashflow_consistency": 100,
    "spending_volatility": "LOW",
    "spending_volatility_score": 0.33,
    "average_savings_rate": 45.55,
}

# Retrieve evidence from pgvector
retrieved_evidence = retrieve_relevant_chunks(
    query=(
        "What evidence describes the applicant's income stability, "
        "financial obligations, payment behavior and cash flow?"
    ),
    top_k=3,
)

explanation = generate_credit_explanation(
    risk_probability=risk_probability,
    risk_band=risk_band,
    shap_factors=shap_factors,
    behavioral_data=behavioral_data,
    retrieved_evidence=retrieved_evidence,
)

print("\n===== GROUNDED CREDIT INTELLIGENCE EXPLANATION =====\n")
print(explanation)