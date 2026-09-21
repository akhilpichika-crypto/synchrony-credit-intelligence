import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)

# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------

DATA_PATH = "ml/data/LoanDataset - LoansDatasest.csv"

df = pd.read_csv(DATA_PATH)

print("Original shape:", df.shape)
print(df["Current_loan_status"].value_counts(dropna=False))


# ---------------------------------------------------------
# 2. CLEAN MONEY COLUMNS
# ---------------------------------------------------------

def clean_money(series):
    return (
        series.astype(str)
        .str.replace("£", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace("nan", np.nan)
        .astype(float)
    )


df["loan_amnt"] = clean_money(df["loan_amnt"])
df["customer_income"] = clean_money(df["customer_income"])


# ---------------------------------------------------------
# 3. NORMALIZE MONETARY VALUES TO PROTOTYPE INR SCALE
# ---------------------------------------------------------

# The source dataset is not treated as representing Indian
# borrowers or as requiring a literal GBP -> INR conversion.
#
# For prototype localization, the source median annual income
# (55,000) is anchored to ₹12,00,000.
#
# The same factor is applied to income and loan amount so that
# loan-to-income ratios remain unchanged.

SOURCE_MEDIAN_INCOME = 55000.0
TARGET_MEDIAN_INCOME_INR = 1200000.0

MONETARY_SCALE_TO_INR = (
    TARGET_MEDIAN_INCOME_INR / SOURCE_MEDIAN_INCOME
)

df["customer_income_inr"] = (
    df["customer_income"] * MONETARY_SCALE_TO_INR
)

df["loan_amount_inr"] = (
    df["loan_amnt"] * MONETARY_SCALE_TO_INR
)

print(
    "\nPrototype monetary scale:",
    round(MONETARY_SCALE_TO_INR, 4)
)

print("\nNormalized annual income distribution:")
print(df["customer_income_inr"].describe())


# ---------------------------------------------------------
# 4. ENGINEER LOAN BURDEN
# ---------------------------------------------------------

df["loan_to_income_ratio"] = (
    df["loan_amount_inr"] / df["customer_income_inr"]
)

df.replace([np.inf, -np.inf], np.nan, inplace=True)


# ---------------------------------------------------------
# 5. TARGET
# ---------------------------------------------------------

df = df.dropna(subset=["Current_loan_status"])

df["target"] = (
    df["Current_loan_status"]
    .astype(str)
    .str.strip()
    .str.upper()
    .map({
        "DEFAULT": 1,
        "NO DEFAULT": 0
    })
)

df = df.dropna(subset=["target"])
df["target"] = df["target"].astype(int)


# ---------------------------------------------------------
# 6. FEATURES
# ---------------------------------------------------------

candidate_features = [
    "customer_age",
    "customer_income_inr",
    "home_ownership",
    "employment_duration",
    "loan_intent",
    "loan_amount_inr",
    "term_years",
    "loan_to_income_ratio",
]

features = [col for col in candidate_features if col in df.columns]

print("\nUsing features:")
print(features)

X = df[features].copy()
y = df["target"]


# ---------------------------------------------------------
# IMPORTANT:
# Do not give the model both the original source monetary
# value and the normalized INR value. They contain the same
# underlying information.
# ---------------------------------------------------------

if "loan_amnt" in X.columns and "loan_amount_inr" in X.columns:
    X = X.drop(columns=["loan_amnt"])

features = X.columns.tolist()


# ---------------------------------------------------------
# 7. IDENTIFY COLUMN TYPES
# ---------------------------------------------------------

numeric_features = X.select_dtypes(include=["number"]).columns.tolist()

categorical_features = [
    col for col in X.columns
    if col not in numeric_features
]


numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])


categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    (
        "onehot",
        OneHotEncoder(
            handle_unknown="ignore"
        )
    ),
])


preprocessor = ColumnTransformer([
    ("num", numeric_pipeline, numeric_features),
    ("cat", categorical_pipeline, categorical_features),
])


# ---------------------------------------------------------
# 8. MODEL
# ---------------------------------------------------------

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=10,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)


pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", model),
])


# ---------------------------------------------------------
# 9. TRAIN / TEST SPLIT
# ---------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)


print("\nTrain:", X_train.shape)
print("Test:", X_test.shape)


# ---------------------------------------------------------
# 10. TRAIN
# ---------------------------------------------------------

pipeline.fit(X_train, y_train)


# ---------------------------------------------------------
# 11. EVALUATE
# ---------------------------------------------------------

pred = pipeline.predict(X_test)
prob = pipeline.predict_proba(X_test)[:, 1]


print("\n--- MODEL RESULTS ---")

print("Accuracy :", round(accuracy_score(y_test, pred), 4))
print("Precision:", round(precision_score(y_test, pred), 4))
print("Recall   :", round(recall_score(y_test, pred), 4))
print("F1       :", round(f1_score(y_test, pred), 4))
print("ROC-AUC  :", round(roc_auc_score(y_test, prob), 4))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, pred))


# ---------------------------------------------------------
# 12. SAVE MODEL + METADATA
# ---------------------------------------------------------

artifact = {
    "pipeline": pipeline,
    "features": features,
    "monetary_scale_to_inr": MONETARY_SCALE_TO_INR,
    "source_median_income": SOURCE_MEDIAN_INCOME,
    "target_median_income_inr": TARGET_MEDIAN_INCOME_INR,
}

joblib.dump(
    artifact,
    "ml/artifacts/loan_risk_model.pkl"
)

print("\nSaved:")
print("ml/artifacts/loan_risk_model.pkl")

# ---------------------------------------------------------
# 13. SANITY CHECK ON A NORMAL NON-DEFAULT APPLICANT
# ---------------------------------------------------------

print("\n--- APPLICANT SANITY CHECK ---")

# Pick a real non-default applicant from the test set
non_default_indices = y_test[y_test == 0].index
sample = X_test.loc[[non_default_indices[0]]].copy()

print("\nApplicant features:")
for column in sample.columns:
    print(f"{column}: {sample[column].iloc[0]}")

annual_income = float(
    sample["customer_income_inr"].iloc[0]
)

print("\n--- REQUESTED LOAN SENSITIVITY ---")

for requested_amount in [
    150000,
    300000,
    500000,
    750000,
    1000000
]:

    test_applicant = sample.copy()

    test_applicant["loan_amount_inr"] = requested_amount

    test_applicant["loan_to_income_ratio"] = (
        requested_amount / annual_income
    )

    risk = pipeline.predict_proba(
        test_applicant
    )[0][1]

    print(
        f"₹{requested_amount:,.0f}"
        f" | Loan/Income: "
        f"{requested_amount / annual_income:.3f}"
        f" | Risk: {risk * 100:.2f}%"
    )