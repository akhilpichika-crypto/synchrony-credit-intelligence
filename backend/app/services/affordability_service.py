import math
import logging

logger = logging.getLogger("credit_intelligence")

# Prototype city living-cost references.
# These are DEMO assumptions, not lender policy or official cost-of-living data.
CITY_LIVING_COST = {
    "Hyderabad": 22000,
    "Bengaluru": 26000,
    "Chennai": 23000,
    "Mumbai": 30000,
    "Delhi": 26000,
    "Pune": 24000,
}

# We preserve 40% of repayment surplus as a safety buffer.
EMI_UTILIZATION_FACTOR = 0.60

# Illustrative prototype APR assumptions.
# These are NOT Synchrony pricing rules or actual lending rates.
PROTOTYPE_APR_BY_RISK = {
    "LOW": 10.0,
    "MEDIUM": 14.0,
    "HIGH": 18.0,
}


def calculate_affordable_emi(
    stable_monthly_income: float,
    observed_monthly_expenses: float,
    existing_monthly_obligations: float,
    city: str,
):
    """
    Estimate sustainable monthly repayment capacity.

    This is a prototype affordability calculation and not
    a lending approval or recommendation.
    """

    if stable_monthly_income < 0:
        raise ValueError("Monthly income cannot be negative")

    if observed_monthly_expenses < 0:
        raise ValueError("Monthly expenses cannot be negative")

    if existing_monthly_obligations < 0:
        raise ValueError("Existing obligations cannot be negative")

    if city not in CITY_LIVING_COST:
        raise ValueError(
            f"Living-cost reference is not configured for {city}"
        )

    city_living_cost = CITY_LIVING_COST[city]

    # Conservatively use whichever expense estimate is higher.
    living_expense_used = max(
        observed_monthly_expenses,
        city_living_cost,
    )

    repayment_surplus = (
        stable_monthly_income
        - living_expense_used
        - existing_monthly_obligations
    )

    # No positive surplus => no estimated EMI capacity.
    if repayment_surplus <= 0:
        affordable_emi = 0
        safety_buffer = 0
    else:
        affordable_emi = (
            repayment_surplus * EMI_UTILIZATION_FACTOR
        )

        safety_buffer = (
            repayment_surplus - affordable_emi
        )

    return {
        "stable_monthly_income": round(
            stable_monthly_income, 2
        ),

        "observed_monthly_expenses": round(
            observed_monthly_expenses, 2
        ),

        "city": city,

        "city_living_cost_reference": round(
            city_living_cost, 2
        ),

        "living_expense_used": round(
            living_expense_used, 2
        ),

        "existing_monthly_obligations": round(
            existing_monthly_obligations, 2
        ),

        "repayment_surplus": round(
            max(0, repayment_surplus), 2
        ),

        "safety_buffer": round(
            safety_buffer, 2
        ),

        "affordable_emi": round(
            affordable_emi, 2
        ),

        "emi_utilization_factor": EMI_UTILIZATION_FACTOR,

        "affordability_status": (
            "POSITIVE_CAPACITY"
            if repayment_surplus > 0
            else "NO_POSITIVE_CAPACITY"
        ),
    }

def calculate_loan_capacity(
    affordable_emi: float,
    annual_apr: float,
    duration_months: int,
):
    """
    Reverse the standard EMI formula to estimate the
    principal supported by the affordable monthly EMI.

    Prototype estimate only.
    """

    if affordable_emi <= 0:
        return 0

    if duration_months <= 0:
        raise ValueError("Duration must be greater than zero")

    if annual_apr < 0:
        raise ValueError("APR cannot be negative")

    # Monthly interest rate
    monthly_rate = annual_apr / (12 * 100)

    # Special case for zero interest
    if monthly_rate == 0:
        return round(
            affordable_emi * duration_months,
            2
        )

    factor = (1 + monthly_rate) ** duration_months

    loan_capacity = (
        affordable_emi
        * (factor - 1)
        / (monthly_rate * factor)
    )

    logger.info(
        "Loan capacity calculated | duration_months=%s | prototype_apr=%.1f",
        duration_months,
        annual_apr,
    )

    return round(loan_capacity, 2)