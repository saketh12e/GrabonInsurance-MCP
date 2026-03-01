"""Mock Pricing API on port 8001.

Lightweight mock insurer pricing service.
"""

import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from insurance_engine.catalog import get_all_products, lookup_by_id
from insurance_engine.pricing import PREMIUM_CAP, PREMIUM_FLOOR, RISK_MULTIPLIERS

load_dotenv()


class PricingRequest(BaseModel):
    """Request body for pricing quote."""

    product_id: str = Field(description="Insurance product ID")
    deal_value: float = Field(gt=0, description="Deal amount in INR")
    risk_tier: str = Field(default="medium", description="User risk tier")


class PricingResponse(BaseModel):
    """Response from pricing API."""

    premium_inr: float = Field(description="Calculated premium in INR")
    coverage_inr: float = Field(description="Coverage amount in INR")
    validity_days: int = Field(description="Policy validity in days")


class ProductInfo(BaseModel):
    """Simplified product info for pricing."""

    id: str
    name: str
    base_premium_rate: float
    coverage_multiplier: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    yield


app = FastAPI(
    title="GrabInsurance Pricing API",
    description="Mock insurer pricing service for premium calculations",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/pricing/quote", response_model=PricingResponse)
async def get_quote(request: PricingRequest) -> PricingResponse:
    """Calculate premium quote for a product.

    Args:
        request: PricingRequest with product_id, deal_value, risk_tier

    Returns:
        PricingResponse with premium_inr, coverage_inr, validity_days

    Raises:
        HTTPException: 400 if product not found or invalid data
    """
    product = lookup_by_id(request.product_id)
    if product is None:
        raise HTTPException(status_code=400, detail=f"Product not found: {request.product_id}")

    risk_tier = request.risk_tier
    if risk_tier not in RISK_MULTIPLIERS:
        risk_tier = "medium"

    # Calculate using exact formula
    base = product.base_premium_rate * request.deal_value
    premium = base * RISK_MULTIPLIERS[risk_tier]
    final_premium = max(PREMIUM_FLOOR, min(PREMIUM_CAP, round(premium)))

    coverage = (request.deal_value * product.coverage_multiplier) / 100

    return PricingResponse(
        premium_inr=float(final_premium),
        coverage_inr=coverage,
        validity_days=30,
    )


@app.get("/pricing/products", response_model=list[ProductInfo])
async def list_products() -> list[ProductInfo]:
    """Get simplified product list with pricing metadata.

    Returns:
        List of products with pricing info
    """
    products = get_all_products()
    return [
        ProductInfo(
            id=p.id,
            name=p.name,
            base_premium_rate=p.base_premium_rate,
            coverage_multiplier=p.coverage_multiplier,
        )
        for p in products
    ]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "pricing-api"}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "GrabInsurance Pricing API",
        "version": "0.1.0",
        "description": "Mock insurer pricing service for premium calculations",
        "endpoints": {
            "get_quote": "POST /pricing/quote",
            "list_products": "GET /pricing/products",
            "health": "GET /health",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
