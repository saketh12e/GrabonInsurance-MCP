"""A/B Testing events API routes."""

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from insurance_engine.ab_testing import (
    get_dashboard_data,
    get_variant,
    record_conversion,
    record_impression,
)
from mcp_server.schemas import ConvertRequest, ConvertResponse, DashboardData

router = APIRouter(prefix="/api/ab-events", tags=["ab-testing"])


class ImpressionRequest(BaseModel):
    """Request for recording an impression."""

    session_id: str = Field(description="Session ID")
    deal_id: str = Field(description="Deal ID")
    user_id: str = Field(description="User ID")
    product_id: str = Field(description="Product ID")
    copy_string: str = Field(description="Generated copy")


class ImpressionResponse(BaseModel):
    """Response after recording impression."""

    success: bool
    session_id: str
    variant: str


@router.post("/impression", response_model=ImpressionResponse)
async def record_ab_impression(request: ImpressionRequest) -> ImpressionResponse:
    """Record an A/B test impression.

    Args:
        request: ImpressionRequest with session details

    Returns:
        ImpressionResponse with assigned variant
    """
    session = await record_impression(
        session_id=request.session_id,
        deal_id=request.deal_id,
        user_id=request.user_id,
        product_id=request.product_id,
        copy_string=request.copy_string,
    )

    return ImpressionResponse(
        success=True,
        session_id=session.session_id,
        variant=session.variant,
    )


@router.post("/convert", response_model=ConvertResponse)
async def convert_session(request: ConvertRequest) -> ConvertResponse:
    """Record a conversion event.

    Called when user clicks "Get Covered" button.

    Args:
        request: ConvertRequest with session_id and product_id

    Returns:
        ConvertResponse with success status and timestamp
    """
    converted_at = await record_conversion(request.session_id, request.product_id)

    if converted_at:
        return ConvertResponse(success=True, converted_at=converted_at)
    else:
        return ConvertResponse(success=False, converted_at=None)


@router.get("/dashboard", response_model=DashboardData)
async def get_ab_dashboard() -> DashboardData:
    """Get A/B testing dashboard metrics.

    Returns:
        DashboardData with variant stats and totals
    """
    return await get_dashboard_data()


@router.get("/variant")
async def get_assigned_variant(session_id: str, product_id: str) -> dict:
    """Get the assigned variant for a session/product combination.

    Args:
        session_id: Session identifier
        product_id: Product identifier

    Returns:
        Dict with variant assignment
    """
    variant = get_variant(session_id, product_id)
    return {"session_id": session_id, "product_id": product_id, "variant": variant}
