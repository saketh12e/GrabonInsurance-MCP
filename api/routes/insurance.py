"""Insurance API routes."""

import os
import uuid
from typing import Literal

import anthropic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from insurance_engine.ab_testing import get_variant, record_impression
from insurance_engine.cart_resolver import classify_deal_with_cart
from insurance_engine.catalog import get_all_products
from insurance_engine.classifier import classify_intent
from insurance_engine.pricing import calculate_premium
from mcp_server.prompts import generate_insurance_copy_prompt
from mcp_server.schemas import (
    CartItem,
    ClassificationResult,
    CopyRequest,
    CopyResponse,
    DealObject,
    InsuranceProduct,
    PremiumQuote,
    QuoteRequest,
    UserHistory,
)

router = APIRouter(prefix="/api", tags=["insurance"])


class ClassifyRequest(BaseModel):
    """Request for deal classification."""

    merchant: str = Field(description="Merchant name")
    category: str = Field(description="Deal category")
    subcategory: str = Field(description="Deal subcategory")
    deal_value: float = Field(description="Deal amount in INR")
    user_history: dict | None = Field(default=None, description="User history")
    cart_items: list[dict] | None = Field(default=None, description="Cart items for multi-cart")


@router.post("/classify", response_model=ClassificationResult)
async def classify_deal(request: ClassifyRequest) -> ClassificationResult:
    """Classify a deal and return top insurance products.

    Args:
        request: ClassifyRequest with deal details

    Returns:
        ClassificationResult with top_products, cart_context, show_offer

    Raises:
        HTTPException: 400 if deal_value is invalid
    """
    if request.deal_value is None or request.deal_value == 0:
        raise HTTPException(status_code=400, detail="invalid_deal_value")

    # Handle multi-cart
    if request.cart_items:
        cart_items = [CartItem(**item) for item in request.cart_items]
        user_history = UserHistory(**(request.user_history or {}))
        deal = DealObject(
            merchant=request.merchant,
            category=request.category,
            subcategory=request.subcategory,
            deal_value=request.deal_value,
            user_history=user_history,
            cart_items=cart_items,
        )
        return await classify_deal_with_cart(deal)

    # Single deal
    return await classify_intent(
        merchant=request.merchant,
        category=request.category,
        subcategory=request.subcategory,
        deal_value=request.deal_value,
        user_history=request.user_history,
    )


@router.post("/quote", response_model=PremiumQuote)
async def get_quote(request: QuoteRequest) -> PremiumQuote:
    """Get premium quote for a product.

    Args:
        request: QuoteRequest with product_id, deal_value, risk_tier

    Returns:
        PremiumQuote with premium_inr, coverage_inr, validity_days

    Raises:
        HTTPException: 400 if invalid request
    """
    try:
        return calculate_premium(
            product_id=request.product_id,
            deal_value=request.deal_value,
            risk_tier=request.risk_tier,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-copy", response_model=CopyResponse)
async def generate_copy(request: CopyRequest) -> CopyResponse:
    """Generate personalized insurance copy.

    Args:
        request: CopyRequest with product details and variant

    Returns:
        CopyResponse with copy_string, variant, session_id
    """
    # Generate session ID
    session_id = str(uuid.uuid4())

    # Get prompt
    prompt_messages = generate_insurance_copy_prompt(
        product_name=request.product_name,
        deal_description=request.deal_description,
        premium_inr=request.premium_inr,
        variant=request.variant,
    )

    # Call Claude API
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        # Fallback copy if no API key
        copy_string = f"{request.deal_description}. Cover for Rs {request.premium_inr:.0f}."
        if len(copy_string) > 120:
            copy_string = copy_string[:117] + "..."
    else:
        try:
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=prompt_messages,
            )
            copy_string = response.content[0].text.strip()
            # Ensure under 120 chars
            if len(copy_string) > 120:
                copy_string = copy_string[:117] + "..."
        except Exception:
            copy_string = f"{request.deal_description}. Cover for Rs {request.premium_inr:.0f}."
            if len(copy_string) > 120:
                copy_string = copy_string[:117] + "..."

    return CopyResponse(
        copy_string=copy_string,
        variant=request.variant,
        session_id=session_id,
    )


@router.get("/catalog", response_model=list[InsuranceProduct])
async def get_catalog() -> list[InsuranceProduct]:
    """Get full insurance catalog.

    Returns:
        List of all insurance products
    """
    return get_all_products()
