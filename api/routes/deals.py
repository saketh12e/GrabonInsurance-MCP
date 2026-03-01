"""Deals API routes."""

import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api", tags=["deals"])


def _get_deals_path() -> Path:
    """Get path to mock deals file."""
    deals_path = os.environ.get("DEALS_PATH", "./data/mock_deals.json")
    path = Path(deals_path)
    if not path.exists():
        path = Path(__file__).parent.parent.parent / "data" / "mock_deals.json"
    return path


@router.get("/deals")
async def get_all_deals() -> list[dict]:
    """Get all 10 mock deals.

    Returns:
        List of all deal objects
    """
    path = _get_deals_path()
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Deals data not found")


@router.get("/deals/{deal_id}")
async def get_deal(deal_id: str) -> dict:
    """Get a specific deal by ID.

    Args:
        deal_id: Deal ID (e.g., D001)

    Returns:
        Deal object

    Raises:
        HTTPException: 404 if deal not found
    """
    path = _get_deals_path()
    try:
        with open(path) as f:
            deals = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Deals data not found")

    for deal in deals:
        if deal.get("deal_id") == deal_id:
            return deal

    raise HTTPException(status_code=404, detail=f"Deal not found: {deal_id}")
