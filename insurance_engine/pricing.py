"""Premium Pricing Engine.

Exact formula from blueprint section 6:
- risk_multipliers = {"low": 0.8, "medium": 1.0, "high": 1.4}
- base = product.base_premium_rate * deal_value
- premium = base * risk_multipliers[risk_tier]
- final = max(19, min(499, round(premium, 0)))
"""

from insurance_engine.catalog import lookup_by_id
from mcp_server.schemas import PremiumQuote

# Risk multipliers for premium calculation
RISK_MULTIPLIERS = {
    "low": 0.8,
    "medium": 1.0,
    "high": 1.4,
}

# Premium bounds
PREMIUM_FLOOR = 19
PREMIUM_CAP = 499


def calculate_premium(
    product_id: str,
    deal_value: float,
    risk_tier: str = "medium",
) -> PremiumQuote:
    """Calculate premium quote for an insurance product.

    Uses the exact formula from blueprint:
    - base = product.base_premium_rate * deal_value
    - premium = base * risk_multipliers[risk_tier]
    - final = max(19, min(499, round(premium)))

    Args:
        product_id: Insurance product ID
        deal_value: Deal amount in INR
        risk_tier: User risk tier (low, medium, high)

    Returns:
        PremiumQuote with premium_inr, coverage_inr, validity_days, policy_type

    Raises:
        ValueError: If product not found or deal_value invalid
    """
    if deal_value is None or deal_value <= 0:
        raise ValueError("invalid_deal_value")

    if risk_tier not in RISK_MULTIPLIERS:
        risk_tier = "medium"

    product = lookup_by_id(product_id)
    if product is None:
        raise ValueError(f"Product not found: {product_id}")

    # Calculate premium using exact formula
    base = product.base_premium_rate * deal_value
    premium = base * RISK_MULTIPLIERS[risk_tier]
    final_premium = max(PREMIUM_FLOOR, min(PREMIUM_CAP, round(premium)))

    # Calculate coverage
    coverage = (deal_value * product.coverage_multiplier) / 100

    return PremiumQuote(
        premium_inr=float(final_premium),
        coverage_inr=coverage,
        validity_days=30,
        policy_type=product.name,
    )


async def get_premium_quote(
    product_id: str,
    deal_value: float,
    risk_tier: str = "medium",
) -> PremiumQuote:
    """Async wrapper for calculate_premium.

    Args:
        product_id: Insurance product ID
        deal_value: Deal amount in INR
        risk_tier: User risk tier

    Returns:
        PremiumQuote
    """
    return calculate_premium(product_id, deal_value, risk_tier)
