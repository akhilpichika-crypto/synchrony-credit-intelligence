import io
import pandas as pd
import numpy as np


def analyze_transactions(file_bytes: bytes):
    """
    Analyze synthetic transaction data and derive behavioral indicators.

    Expected CSV columns:
    date, description, amount, type
    """

    df = pd.read_csv(io.BytesIO(file_bytes))

    required_columns = {"date", "description", "amount", "type"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            "CSV must contain: date, description, amount, type"
        )

    if df.empty:
        raise ValueError("Transaction file is empty")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    df = df.dropna(subset=["date", "amount"])

    if df.empty:
        raise ValueError("No valid transactions found")

    df["type"] = df["type"].str.lower().str.strip()

    if not df["type"].isin(["credit", "debit"]).all():
        raise ValueError("Transaction type must be credit or debit")

    df["month"] = df["date"].dt.to_period("M").astype(str)

    credits = df[df["type"] == "credit"]
    debits = df[df["type"] == "debit"]

    monthly_income = credits.groupby("month")["amount"].sum()
    monthly_expenses = debits.groupby("month")["amount"].sum()

    months = sorted(df["month"].unique())

    income = monthly_income.reindex(months, fill_value=0)
    expenses = monthly_expenses.reindex(months, fill_value=0)

    # ---------- Income stability ----------
    mean_income = income.mean()

    if mean_income > 0:
        income_cv = income.std(ddof=0) / mean_income
        income_stability = max(0, min(100, 100 * (1 - income_cv)))
    else:
        income_stability = 0

    # ---------- Cash-flow consistency ----------
    monthly_surplus = income - expenses

    if len(monthly_surplus) > 0:
        positive_month_ratio = (monthly_surplus >= 0).mean()
        cashflow_consistency = positive_month_ratio * 100
    else:
        cashflow_consistency = 0

    # ---------- Spending volatility ----------
    mean_expense = expenses.mean()

    if mean_expense > 0:
        expense_cv = expenses.std(ddof=0) / mean_expense
        spending_volatility_score = min(100, expense_cv * 100)
    else:
        spending_volatility_score = 0

    if spending_volatility_score < 15:
        spending_volatility = "LOW"
    elif spending_volatility_score < 30:
        spending_volatility = "MEDIUM"
    else:
        spending_volatility = "HIGH"

    # ---------- Savings behavior ----------
    savings_rates = []

    for month in months:
        month_income = income.loc[month]
        month_expense = expenses.loc[month]

        if month_income > 0:
            savings_rates.append(
                (month_income - month_expense) / month_income
            )

    if savings_rates:
        average_savings_rate = np.mean(savings_rates) * 100
    else:
        average_savings_rate = 0

    # Keep presentation range sensible.
    average_savings_rate = max(-100, min(100, average_savings_rate))

    return {
        "data_source": "synthetic_transaction_statement",
        "months_analyzed": len(months),
        "total_transactions": int(len(df)),
        "income_stability": round(float(income_stability), 2),
        "cashflow_consistency": round(float(cashflow_consistency), 2),
        "spending_volatility": spending_volatility,
        "spending_volatility_score": round(
            float(spending_volatility_score), 2
        ),
        "average_savings_rate": round(
            float(average_savings_rate), 2
        ),
    }