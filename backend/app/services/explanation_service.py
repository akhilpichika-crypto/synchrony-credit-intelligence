import numpy as np
import pandas as pd
import shap


def explain_prediction(model, applicant_data: dict, top_n: int = 5):
    """
    Generate SHAP explanations and aggregate one-hot encoded
    categorical features back to their original business features.
    """

    input_df = pd.DataFrame([applicant_data])

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["model"]

    # Apply the exact preprocessing learned during training
    transformed_input = preprocessor.transform(input_df)

    # Calculate SHAP values for the Random Forest
    explainer = shap.TreeExplainer(classifier)
    shap_values = explainer.shap_values(transformed_input)

    # Extract SHAP values for class 1 = bad-risk
    if isinstance(shap_values, list):
        risk_shap_values = shap_values[1][0]
    else:
        values = np.asarray(shap_values)

        if values.ndim == 3:
            risk_shap_values = values[0, :, 1]
        else:
            risk_shap_values = values[0]

    feature_names = preprocessor.get_feature_names_out()

    # Original input column names
    original_features = list(applicant_data.keys())

    # Aggregate transformed features back to original features
    aggregated = {feature: 0.0 for feature in original_features}

    for transformed_feature, shap_value in zip(
        feature_names, risk_shap_values
    ):
        clean_name = (
            transformed_feature
            .replace("num__", "")
            .replace("cat__", "")
        )

        # Numerical columns normally match directly.
        if clean_name in aggregated:
            original_feature = clean_name
        else:
            # One-hot names look like:
            # checking_status_A11
            # credit_history_A34
            #
            # Find the longest matching original feature name.
            matches = [
                feature
                for feature in original_features
                if clean_name.startswith(feature + "_")
            ]

            if not matches:
                continue

            original_feature = max(matches, key=len)

        aggregated[original_feature] += float(shap_value)

    contributions = []

    for feature, impact in aggregated.items():
        contributions.append(
            {
                "feature": feature,
                "impact": round(impact, 4),
                "direction": (
                    "increases risk"
                    if impact > 0
                    else "decreases risk"
                )
            }
        )

    # Rank by magnitude of impact
    contributions.sort(
        key=lambda item: abs(item["impact"]),
        reverse=True
    )

    return contributions[:top_n]