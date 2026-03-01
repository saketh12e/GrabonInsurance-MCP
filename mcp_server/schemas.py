"""Pydantic v2 models for GrabInsurance MCP Server.

All inputs and outputs are validated at every boundary using these schemas.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class CartItem(BaseModel):
    """A single item in a multi-item cart."""

    merchant: str = Field(description="Merchant name for this cart item")
    category: str = Field(description="Product category: travel, electronics, food, health, fashion")
    subcategory: str = Field(description="Specific subcategory: flight, phone, delivery, etc.")
    deal_value: float = Field(description="Deal amount in INR for this item")


class UserHistory(BaseModel):
    """User purchase history and risk profile."""

    risk_tier: Literal["low", "medium", "high"] = Field(
        default="medium", description="User risk tier affecting premium calculation"
    )
    total_purchases: int = Field(default=0, description="Total number of purchases by user")
    categories_bought: list[str] = Field(
        default_factory=list, description="List of categories user has purchased from"
    )


class DealObject(BaseModel):
    """Input object representing a deal for classification."""

    merchant: str = Field(description="Merchant name e.g. 'IndiGo', 'Samsung', 'Zomato'")
    category: str = Field(description="One of: travel, electronics, food, health, fashion, or MULTI")
    subcategory: str = Field(description="Specific subcategory: flight, hotel, gadget, phone, etc.")
    deal_value: float = Field(description="Deal amount in INR")
    user_history: UserHistory = Field(
        default_factory=UserHistory, description="User's purchase history and risk profile"
    )
    cart_items: Optional[list[CartItem]] = Field(
        default=None, description="Individual items for multi-category carts"
    )


class InsuranceMatch(BaseModel):
    """A matched insurance product with confidence score."""

    product_id: str = Field(description="Insurance product ID e.g. TRVL_CANCEL, ELEC_SCREEN")
    product_name: str = Field(description="Human-readable product name")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0"
    )
    reason: str = Field(description="One sentence explanation for this match")


class ClassificationResult(BaseModel):
    """Output from the classify_intent tool."""

    top_products: list[InsuranceMatch] = Field(
        max_length=2, description="Top 1-2 insurance products matched, max 2"
    )
    cart_context: Literal["single", "multi", "ambiguous"] = Field(
        description="Whether deal is single item, multi-cart, or ambiguous"
    )
    show_offer: bool = Field(
        description="False if deal_value < 200, True otherwise"
    )
    fallback_used: bool = Field(
        default=False,
        description="True if Claude API timed out and rules were used instead",
    )
    reason: Optional[str] = Field(
        default=None, description="Reason if show_offer is False"
    )


class InsuranceProduct(BaseModel):
    """Insurance product from catalog."""

    id: str = Field(description="Unique product identifier")
    name: str = Field(description="Human-readable product name")
    category_triggers: list[str] = Field(description="Categories that trigger this product")
    subcategory_triggers: list[str] = Field(
        description="Subcategories that trigger this product, * for wildcard"
    )
    base_premium_rate: float = Field(description="Base rate for premium calculation")
    coverage_multiplier: int = Field(description="Multiplier for coverage calculation")
    description: str = Field(description="Product description")


class PremiumQuote(BaseModel):
    """Output from the get_premium_quote tool."""

    premium_inr: float = Field(
        ge=19, le=499, description="Calculated premium in INR, floored at 19, capped at 499"
    )
    coverage_inr: float = Field(description="Coverage amount in INR")
    validity_days: int = Field(default=30, description="Policy validity in days")
    policy_type: str = Field(description="Type of policy from product catalog")


class QuoteRequest(BaseModel):
    """Request body for getting a premium quote."""

    product_id: str = Field(description="Insurance product ID")
    deal_value: float = Field(gt=0, description="Deal amount in INR")
    risk_tier: Literal["low", "medium", "high"] = Field(
        default="medium", description="User's risk tier"
    )


class CopyRequest(BaseModel):
    """Request body for generating insurance copy."""

    product_id: str = Field(description="Insurance product ID")
    product_name: str = Field(description="Human-readable product name")
    deal_description: str = Field(
        description="Description including merchant, destination, amount"
    )
    premium_inr: float = Field(description="Premium amount in INR")
    variant: Literal["urgency", "value", "social_proof"] = Field(
        description="A/B variant type affecting copy framing"
    )


class CopyResponse(BaseModel):
    """Response containing generated insurance copy."""

    copy_string: str = Field(max_length=120, description="Generated copy under 120 characters")
    variant: str = Field(description="A/B variant used for this copy")
    session_id: str = Field(description="Session ID for A/B tracking")


class ConvertRequest(BaseModel):
    """Request body for recording a conversion event."""

    session_id: str = Field(description="A/B session ID")
    product_id: str = Field(description="Product that was converted")


class ConvertResponse(BaseModel):
    """Response for conversion recording."""

    success: bool = Field(description="Whether conversion was recorded successfully")
    converted_at: Optional[datetime] = Field(
        default=None, description="Timestamp of conversion"
    )


class ABSession(BaseModel):
    """A/B testing session record."""

    session_id: str = Field(description="Unique session identifier")
    deal_id: str = Field(description="Deal being shown")
    user_id: str = Field(description="User seeing the offer")
    variant: Literal["urgency", "value", "social_proof"] = Field(
        description="Assigned A/B variant"
    )
    product_id: str = Field(description="Insurance product shown")
    copy_string: str = Field(description="Generated copy string")
    shown_at: datetime = Field(description="When offer was shown")
    converted: bool = Field(default=False, description="Whether user converted")
    converted_at: Optional[datetime] = Field(
        default=None, description="When conversion happened"
    )


class VariantStats(BaseModel):
    """Statistics for a single A/B variant."""

    variant: str = Field(description="Variant name: urgency, value, or social_proof")
    impressions: int = Field(description="Number of times variant was shown")
    conversions: int = Field(description="Number of conversions")
    cvr_percent: float = Field(description="Conversion rate as percentage")
    is_best: bool = Field(default=False, description="Whether this is the best performing variant")


class DashboardData(BaseModel):
    """Complete A/B testing dashboard data."""

    variants: list[VariantStats] = Field(description="Stats for each variant")
    total_impressions: int = Field(description="Total impressions across all variants")
    total_conversions: int = Field(description="Total conversions across all variants")
    overall_cvr_percent: float = Field(description="Overall conversion rate")
