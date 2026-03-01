"""API Routes for GrabInsurance."""

from api.routes.ab_events import router as ab_events_router
from api.routes.deals import router as deals_router
from api.routes.insurance import router as insurance_router

__all__ = ["deals_router", "insurance_router", "ab_events_router"]
