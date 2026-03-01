"""MCP Tools for GrabInsurance.

Contains classify_intent and get_premium_quote tools with full docstrings,
typed inputs, Pydantic output models, try/except with graceful fallback,
and 5-second timeout on Claude API calls.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

import anthropic

from mcp_server.schemas import (
    ClassificationResult,
    DealObject,
    InsuranceMatch,
    InsuranceProduct,
    PremiumQuote,
    UserHistory,
)

# Risk multipliers for premium calculation
RISK_MULTIPLIERS = {"low": 0.8, "medium": 1.0, "high": 1.4}

# Rule-based classification mappings from blueprint section 6
CLASSIFICATION_RULES: dict[tuple[str, str], list[tuple[str, float]]] = {
    ("travel", "flight"): [("TRVL_CANCEL", 0.92)],
    ("travel", "hotel"): [("TRVL_RETURN", 0.85), ("TRVL_CANCEL", 0.65)],
    ("travel", "international"): [("TRVL_MED", 0.95), ("TRVL_CANCEL", 0.88)],
    ("travel", "train"): [("TRVL_CANCEL", 0.80), ("TRVL_RETURN", 0.60)],
    ("travel", "bus"): [("TRVL_CANCEL", 0.75), ("TRVL_RETURN", 0.55)],
    ("electronics", "phone"): [("ELEC_SCREEN", 0.90)],
    ("electronics", "tablet"): [("ELEC_SCREEN", 0.90)],
    ("electronics", "laptop"): [("ELEC_WARRANTY", 0.90), ("PURCHASE_PROTECT", 0.60)],
    ("electronics", "tv"): [("ELEC_WARRANTY", 0.90), ("PURCHASE_PROTECT", 0.60)],
    ("electronics", "gadget"): [("ELEC_WARRANTY", 0.90), ("PURCHASE_PROTECT", 0.60)],
    ("food", "delivery"): [("FOOD_ACCIDENT", 0.70), ("PURCHASE_PROTECT", 0.45)],
    ("health", "pharmacy"): [("HEALTH_OPD", 0.88), ("PURCHASE_PROTECT", 0.55)],
    ("health", "clinic"): [("HEALTH_OPD", 0.88), ("PURCHASE_PROTECT", 0.55)],
    ("health", "diagnostics"): [("HEALTH_OPD", 0.88), ("PURCHASE_PROTECT", 0.55)],
    ("fashion", "*"): [("PURCHASE_PROTECT", 0.40)],
}

# Category-level fallback rules
CATEGORY_RULES: dict[str, list[tuple[str, float]]] = {
    "travel": [("TRVL_CANCEL", 0.70)],
    "electronics": [("ELEC_WARRANTY", 0.65)],
    "food": [("FOOD_ACCIDENT", 0.50), ("PURCHASE_PROTECT", 0.35)],
    "health": [("HEALTH_OPD", 0.70)],
    "fashion": [("PURCHASE_PROTECT", 0.40)],
}


def _load_catalog() -> list[InsuranceProduct]:
    """Load insurance catalog from JSON file."""
    catalog_path = os.environ.get("CATALOG_PATH", "./data/insurance_catalog.json")
    path = Path(catalog_path)
    if not path.exists():
        # Try relative to script location
        path = Path(__file__).parent.parent / "data" / "insurance_catalog.json"

    with open(path) as f:
        data = json.load(f)
    return [InsuranceProduct(**item) for item in data]


def _get_product_by_id(product_id: str, catalog: list[InsuranceProduct]) -> InsuranceProduct | None:
    """Get a product from catalog by ID."""
    for product in catalog:
        if product.id == product_id:
            return product
    return None


def _apply_rules(
    category: str,
    subcategory: str,
    deal_value: float,
    catalog: list[InsuranceProduct],
) -> list[InsuranceMatch]:
    """Apply rule-based classification logic.

    Args:
        category: Deal category (travel, electronics, food, health, fashion)
        subcategory: Deal subcategory (flight, phone, etc.)
        deal_value: Deal amount in INR
        catalog: List of insurance products

    Returns:
        List of InsuranceMatch objects, max 2
    """
    matches: list[InsuranceMatch] = []
    category_lower = category.lower()
    subcategory_lower = subcategory.lower()

    # Try exact match first
    key = (category_lower, subcategory_lower)
    if key in CLASSIFICATION_RULES:
        rules = CLASSIFICATION_RULES[key]
    elif (category_lower, "*") in CLASSIFICATION_RULES:
        # Wildcard subcategory match
        rules = CLASSIFICATION_RULES[(category_lower, "*")]
    elif category_lower in CATEGORY_RULES:
        # Fall back to category-level rules
        rules = CATEGORY_RULES[category_lower]
        # Log unrecognized subcategory to stderr
        print(f"Unrecognized subcategory '{subcategory}' for category '{category}', using category rules", file=sys.stderr)
    else:
        # Unknown category - will trigger Claude fallback
        return []

    for product_id, confidence in rules:
        product = _get_product_by_id(product_id, catalog)
        if product is None:
            continue

        # Special rules based on deal value
        if product_id == "TRVL_MED" and deal_value <= 8000 and subcategory_lower != "international":
            # TRVL_MED only for high-value travel or international
            continue
        if product_id == "ELEC_WARRANTY" and category_lower == "electronics" and subcategory_lower in ("phone", "tablet"):
            # For phone/tablet, only add warranty if deal_value > 5000
            if deal_value > 5000:
                matches.append(InsuranceMatch(
                    product_id=product_id,
                    product_name=product.name,
                    confidence=0.85,
                    reason=f"Extended warranty for high-value {subcategory}",
                ))
            continue

        matches.append(InsuranceMatch(
            product_id=product_id,
            product_name=product.name,
            confidence=confidence,
            reason=f"Matched {category}/{subcategory} deal pattern",
        ))

    # Add TRVL_MED for flight if deal_value > 8000
    if category_lower == "travel" and subcategory_lower == "flight" and deal_value > 8000:
        product = _get_product_by_id("TRVL_MED", catalog)
        if product and not any(m.product_id == "TRVL_MED" for m in matches):
            matches.append(InsuranceMatch(
                product_id="TRVL_MED",
                product_name=product.name,
                confidence=0.75,
                reason="Medical cover for high-value flight booking",
            ))

    # Add ELEC_WARRANTY for high-value phone/tablet (>5000) - blueprint section 6
    if category_lower == "electronics" and subcategory_lower in ("phone", "tablet") and deal_value > 5000:
        product = _get_product_by_id("ELEC_WARRANTY", catalog)
        if product and not any(m.product_id == "ELEC_WARRANTY" for m in matches):
            matches.append(InsuranceMatch(
                product_id="ELEC_WARRANTY",
                product_name=product.name,
                confidence=0.85,
                reason=f"Extended warranty for high-value {subcategory}",
            ))

    # Sort by confidence and limit to 2
    matches.sort(key=lambda m: m.confidence, reverse=True)
    return matches[:2]


async def _claude_classify(
    deal: DealObject,
    catalog: list[InsuranceProduct],
    timeout_seconds: float = 5.0,
) -> list[InsuranceMatch] | None:
    """Use Claude API for classification with timeout.

    Args:
        deal: The deal object to classify
        catalog: Insurance product catalog
        timeout_seconds: Timeout for Claude API call

    Returns:
        List of InsuranceMatch or None if timeout/error
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    catalog_text = json.dumps([p.model_dump() for p in catalog], indent=2)

    prompt = f"""You are an insurance classification system. Given a deal, select the top 1-2 most relevant insurance products.

DEAL:
- Merchant: {deal.merchant}
- Category: {deal.category}
- Subcategory: {deal.subcategory}
- Deal Value: Rs {deal.deal_value}
- User Risk Tier: {deal.user_history.risk_tier}

INSURANCE CATALOG:
{catalog_text}

Return a JSON array of matches with this structure:
[{{"product_id": "...", "product_name": "...", "confidence": 0.0-1.0, "reason": "one sentence"}}]

Rules:
- Maximum 2 products
- Electronics cover only for items > Rs 5000
- Travel insurance has highest priority in multi-category scenarios
- Return empty array [] if no good match

Return ONLY the JSON array, no other text."""

    try:
        client = anthropic.AsyncAnthropic(api_key=api_key)

        async def call_api():
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text

        result = await asyncio.wait_for(call_api(), timeout=timeout_seconds)

        # Parse JSON response
        data = json.loads(result.strip())
        matches = []
        for item in data[:2]:
            matches.append(InsuranceMatch(
                product_id=item["product_id"],
                product_name=item["product_name"],
                confidence=min(1.0, max(0.0, float(item["confidence"]))),
                reason=item["reason"],
            ))
        return matches

    except asyncio.TimeoutError:
        print("Claude API timeout during classification", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Claude API error during classification: {e}", file=sys.stderr)
        return None


async def classify_intent(
    merchant: str,
    category: str,
    subcategory: str,
    deal_value: float,
    user_history: dict[str, Any] | None = None,
) -> ClassificationResult:
    """Classify deal intent and return top insurance products.

    Takes a deal object and returns the top 2 insurance products with confidence scores.
    Uses rule-based classification first, falls back to Claude API if needed.

    Args:
        merchant: Merchant name e.g. "IndiGo", "Samsung", "Zomato"
        category: One of travel, electronics, food, health, fashion
        subcategory: Specific subcategory like flight, hotel, gadget, phone
        deal_value: Deal amount in INR
        user_history: Dict with keys total_purchases, categories_bought, risk_tier

    Returns:
        ClassificationResult with top_products, cart_context, show_offer, fallback_used

    Raises:
        ValueError: If deal_value is 0 or None
    """
    # Validate deal_value
    if deal_value is None or deal_value == 0:
        raise ValueError("invalid_deal_value")

    # Check minimum threshold
    if deal_value < 200:
        return ClassificationResult(
            top_products=[],
            cart_context="single",
            show_offer=False,
            fallback_used=False,
            reason="deal_value_below_threshold",
        )

    # Parse user history with defaults
    if user_history is None:
        user_history = {}
    history = UserHistory(
        risk_tier=user_history.get("risk_tier", "medium"),
        total_purchases=user_history.get("total_purchases", 0),
        categories_bought=user_history.get("categories_bought", []),
    )

    # Build deal object
    deal = DealObject(
        merchant=merchant,
        category=category,
        subcategory=subcategory,
        deal_value=deal_value,
        user_history=history,
    )

    # Determine cart context
    cart_context = "single"
    if category.upper() == "MULTI" or merchant.startswith("CART:"):
        cart_context = "multi"

    # Load catalog
    try:
        catalog = _load_catalog()
    except Exception as e:
        print(f"Error loading catalog: {e}", file=sys.stderr)
        return ClassificationResult(
            top_products=[],
            cart_context=cart_context,
            show_offer=False,
            fallback_used=True,
            reason="catalog_load_error",
        )

    # Apply rule-based classification
    matches = _apply_rules(category, subcategory, deal_value, catalog)
    fallback_used = False

    # If no matches or low confidence, try Claude API
    if not matches or (matches and matches[0].confidence < 0.35):
        # Check if category is unknown
        if category.lower() not in CATEGORY_RULES and category.upper() != "MULTI":
            claude_matches = await _claude_classify(deal, catalog)
            if claude_matches:
                matches = claude_matches
            else:
                # Claude failed, use PURCHASE_PROTECT as universal fallback
                fallback_used = True
                product = _get_product_by_id("PURCHASE_PROTECT", catalog)
                if product:
                    matches = [InsuranceMatch(
                        product_id="PURCHASE_PROTECT",
                        product_name=product.name,
                        confidence=0.30,
                        reason="Universal fallback for unrecognized category",
                    )]

    # Fashion always marks fallback_used due to low confidence
    if category.lower() == "fashion":
        fallback_used = True

    return ClassificationResult(
        top_products=matches,
        cart_context=cart_context,
        show_offer=True,
        fallback_used=fallback_used,
    )


async def get_premium_quote(
    product_id: str,
    deal_value: float,
    risk_tier: str = "medium",
) -> PremiumQuote:
    """Calculate premium quote for an insurance product.

    Returns a premium quote based on the product's base rate, deal value,
    and user's risk tier. Premium is floored at Rs 19 and capped at Rs 499.

    Args:
        product_id: Insurance product ID from catalog
        deal_value: Deal amount in INR
        risk_tier: User risk tier (low, medium, high)

    Returns:
        PremiumQuote with premium_inr, coverage_inr, validity_days, policy_type

    Raises:
        ValueError: If product_id not found or deal_value invalid
    """
    # Validate deal_value
    if deal_value is None or deal_value <= 0:
        raise ValueError("invalid_deal_value")

    # Validate risk_tier
    if risk_tier not in RISK_MULTIPLIERS:
        risk_tier = "medium"

    # Load catalog and find product
    try:
        catalog = _load_catalog()
    except Exception as e:
        raise ValueError(f"Failed to load catalog: {e}")

    product = _get_product_by_id(product_id, catalog)
    if product is None:
        raise ValueError(f"Product not found: {product_id}")

    # Calculate premium using formula from blueprint
    # base = product.base_premium_rate * deal_value
    # premium = base * risk_multipliers[risk_tier]
    # final = max(19, min(499, round(premium, 0)))
    base = product.base_premium_rate * deal_value
    premium = base * RISK_MULTIPLIERS[risk_tier]
    final_premium = max(19, min(499, round(premium)))

    # Calculate coverage
    coverage = (deal_value * product.coverage_multiplier) / 100

    return PremiumQuote(
        premium_inr=final_premium,
        coverage_inr=coverage,
        validity_days=30,
        policy_type=product.name,
    )
