"""Main API server on port 8000.

FastAPI bridge between React frontend and MCP logic.
CORS enabled for localhost:5173.
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.ab_events import router as ab_events_router
from api.routes.deals import router as deals_router
from api.routes.insurance import router as insurance_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="GrabInsurance API",
    description="API bridge for contextual embedded insurance at deal redemption",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS - enabled for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(deals_router)
app.include_router(insurance_router)
app.include_router(ab_events_router)


@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "grabinsurance-api"}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "GrabInsurance API",
        "version": "0.1.0",
        "description": "Contextual embedded insurance at deal redemption",
        "endpoints": {
            "deals": "/api/deals",
            "classify": "/api/classify",
            "quote": "/api/quote",
            "generate_copy": "/api/generate-copy",
            "catalog": "/api/catalog",
            "ab_dashboard": "/api/ab-events/dashboard",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
