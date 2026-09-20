import pandas as pd

# Load UCI Statlog German Credit dataset
X = pd.read_csv("ml/data/features.csv")
y = pd.read_csv("ml/data/target.csv")
X = X.rename(columns={
    "Attribute1": "checking_status",
    "Attribute2": "duration_months",
    "Attribute3": "credit_history",
    "Attribute4": "purpose",
    "Attribute5": "credit_amount",
    "Attribute6": "savings_status",
    "Attribute7": "employment_status",
    "Attribute8": "installment_rate",
    "Attribute9": "personal_status",
    "Attribute10": "other_debtors",
    "Attribute11": "residence_duration",
    "Attribute12": "property",
    "Attribute13": "age",
    "Attribute14": "other_installment_plans",
    "Attribute15": "housing",
    "Attribute16": "existing_credits",
    "Attribute17": "job",
    "Attribute18": "dependents",
    "Attribute19": "telephone",
    "Attribute20": "foreign_worker"
})
import os

os.makedirs("ml/data", exist_ok=True)

X.to_csv("ml/data/features.csv", index=False)
y.to_csv("ml/data/target.csv", index=False)

print("Dataset saved locally.")

print("Dataset shape:", X.shape)

print("\nFeature names:")
print(X.columns.tolist())

print("\nFirst 5 rows:")
print(X.head())

print("\nTarget distribution:")
print(y.value_counts())

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

# Convert target:
# UCI: 1 = good, 2 = bad
# Our model: 0 = good, 1 = bad
y = y["class"].map({1: 0, 2: 1})

# Identify categorical and numerical columns
categorical_columns = X.select_dtypes(include=["object"]).columns.tolist()
numerical_columns = X.select_dtypes(exclude=["object"]).columns.tolist()

print("\nCategorical columns:", categorical_columns)
print("Numerical columns:", numerical_columns)

# FIRST split the data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", X_train.shape[0])
print("Testing samples:", X_test.shape[0])

# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numerical_columns),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_columns)
    ]
)

# Complete ML pipeline
model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=1000))
    ]
)

# Train
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

# Evaluation
print("\n--- Logistic Regression Results ---")
print("Accuracy :", round(accuracy_score(y_test, y_pred), 3))
print("Precision:", round(precision_score(y_test, y_pred), 3))
print("Recall   :", round(recall_score(y_test, y_pred), 3))
print("F1 Score :", round(f1_score(y_test, y_pred), 3))
print("ROC-AUC  :", round(roc_auc_score(y_test, y_prob), 3))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

from sklearn.ensemble import RandomForestClassifier

# Random Forest pipeline
rf_model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            class_weight="balanced",
            random_state=42
        ))
    ]
)

# Train Random Forest
rf_model.fit(X_train, y_train)

# Predictions
rf_pred = rf_model.predict(X_test)
rf_prob = rf_model.predict_proba(X_test)[:, 1]

print("\n--- Random Forest Results ---")
print("Accuracy :", round(accuracy_score(y_test, rf_pred), 3))
print("Precision:", round(precision_score(y_test, rf_pred), 3))
print("Recall   :", round(recall_score(y_test, rf_pred), 3))
print("F1 Score :", round(f1_score(y_test, rf_pred), 3))
print("ROC-AUC  :", round(roc_auc_score(y_test, rf_prob), 3))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, rf_pred))

import joblib
import os

os.makedirs("ml/artifacts", exist_ok=True)

joblib.dump(
    rf_model,
    "ml/artifacts/credit_risk_model.pkl"
)

print("\nModel saved to ml/artifacts/credit_risk_model.pkl")