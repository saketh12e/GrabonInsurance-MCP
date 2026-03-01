"""GrabInsurance MCP Server.

FastMCP server with stdio transport for Claude Desktop integration.
Registers all tools, resources, and prompts for contextual embedded
insurance at deal redemption.
"""

import os
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from mcp_server.prompts import generate_insurance_copy_prompt, get_copy_system_message
from mcp_server.resources import get_insurance_catalog
from mcp_server.tools import classify_intent, get_premium_quote

# Load environment variables
load_dotenv()

# Create FastMCP server instance
mcp = FastMCP(
    "GrabInsurance",
    instructions="Contextual embedded insurance at deal redemption for GrabOn"
)


@mcp.tool()
async def classify_deal_intent(
    merchant: str,
    category: str,
    subcategory: str,
    deal_value: float,
    user_history: dict[str, Any] | None = None,
) -> dict:
    """Classify deal intent and return top insurance products.

    Takes a deal object and returns the top 2 insurance products with confidence scores.
    Uses rule-based classification first, falls back to Claude API if category is unknown.

    Args:
        merchant: Merchant name e.g. "IndiGo", "Samsung", "Zomato"
        category: One of travel, electronics, food, health, fashion
        subcategory: Specific subcategory like flight, hotel, gadget, phone
        deal_value: Deal amount in INR
        user_history: Optional dict with risk_tier, total_purchases, categories_bought

    Returns:
        ClassificationResult with top_products, cart_context, show_offer, fallback_used
    """
    try:
        result = await classify_intent(
            merchant=merchant,
            category=category,
            subcategory=subcategory,
            deal_value=deal_value,
            user_history=user_history,
        )
        return result.model_dump()
    except ValueError as e:
        return {
            "error": str(e),
            "top_products": [],
            "cart_context": "single",
            "show_offer": False,
            "fallback_used": True,
        }
    except Exception as e:
        return {
            "error": f"Classification failed: {e}",
            "top_products": [],
            "cart_context": "single",
            "show_offer": False,
            "fallback_used": True,
        }


@mcp.tool()
async def get_insurance_quote(
    product_id: str,
    deal_value: float,
    risk_tier: str = "medium",
) -> dict:
    """Calculate premium quote for an insurance product.

    Returns a premium quote based on the product's base rate, deal value,
    and user's risk tier. Premium is floored at Rs 19 and capped at Rs 499.

    Args:
        product_id: Insurance product ID from catalog (e.g., TRVL_CANCEL, ELEC_SCREEN)
        deal_value: Deal amount in INR
        risk_tier: User risk tier (low, medium, high)

    Returns:
        PremiumQuote with premium_inr, coverage_inr, validity_days, policy_type
    """
    try:
        result = await get_premium_quote(
            product_id=product_id,
            deal_value=deal_value,
            risk_tier=risk_tier,
        )
        return result.model_dump()
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Quote calculation failed: {e}"}


@mcp.resource("insurance://catalog")
def insurance_catalog() -> str:
    """Return the full insurance product catalog.

    This resource provides Claude with complete product context including
    all 8 insurance products with their triggers, rates, and descriptions.
    Load this before performing any classification.
    """
    return get_insurance_catalog()


@mcp.prompt()
def generate_copy(
    product_name: str,
    deal_description: str,
    premium_inr: float,
    variant: str = "value",
) -> list[dict]:
    """Generate personalized insurance copy for a deal.

    Creates a prompt that instructs Claude to generate one copy string under
    120 characters. The copy mentions the deal amount and premium explicitly.

    Args:
        product_name: Name of the insurance product
        deal_description: Description including merchant, destination, amount
        premium_inr: Premium amount in INR
        variant: A/B variant type (urgency, value, or social_proof)

    Returns:
        Message list for Claude API with few-shot examples and variant framing
    """
    # Validate variant
    valid_variants = ("urgency", "value", "social_proof")
    if variant not in valid_variants:
        variant = "value"

    return generate_insurance_copy_prompt(
        product_name=product_name,
        deal_description=deal_description,
        premium_inr=premium_inr,
        variant=variant,  # type: ignore
    )


if __name__ == "__main__":
    # Run with stdio transport for Claude Desktop
    mcp.run(transport="stdio")
