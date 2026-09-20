import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

client = genai.Client(api_key=api_key)


def generate_credit_explanation(
    risk_probability: float,
    risk_band: str,
    shap_factors: list,
    behavioral_data: dict,
    retrieved_evidence: list,
):
    """
    Generate a grounded explanation of the credit assessment.

    Gemini explains the supplied evidence only.
    It does not calculate a new credit score or make an
    approval/rejection decision.
    """

    evidence_text = "\n\n".join(
        [
            f"Document: {item['document_name']}\n"
            f"Chunk: {item['chunk_index']}\n"
            f"Evidence: {item['content']}"
            for item in retrieved_evidence
        ]
    )

    prompt = f"""
You are an explainability assistant for a prototype credit
intelligence system.

IMPORTANT RULES:
1. Use ONLY the information supplied below.
2. Do not invent applicant information.
3. Do not calculate or modify the risk probability.
4. Do not approve or reject the applicant.
5. Do not recommend whether credit should be granted.
6. Clearly distinguish model output from supplementary evidence.
7. Treat behavioral and document information as synthetic
   demonstration data.
8. If evidence is insufficient, explicitly say so.
9. SHAP factors represent model contributions, not causal relationships.
   Positive SHAP values contribute toward a higher model risk output,
   while negative SHAP values contribute toward a lower model risk output.
   Describe them as model contributions, not real-world increases or
   decreases in the applicant's actual credit risk.
10. Produce a concise, professional, transparent explanation.

MODEL OUTPUT:
Risk probability: {risk_probability:.2%}
Risk band: {risk_band}

TOP MODEL CONTRIBUTING FACTORS:
{shap_factors}

SYNTHETIC BEHAVIORAL INDICATORS:
{behavioral_data}

RETRIEVED SYNTHETIC DOCUMENT EVIDENCE:
{evidence_text}

Generate the explanation using these sections:

Risk Assessment
Model Contributing Factors
Alternative Data Insights
Supporting Document Evidence
Transparency Note
"""

    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt
    )

    return interaction.output_text