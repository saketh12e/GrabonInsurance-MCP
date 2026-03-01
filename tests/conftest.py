"""Pytest configuration and fixtures for GrabInsurance tests."""

import os
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set environment variables for tests
os.environ.setdefault("CATALOG_PATH", str(Path(__file__).parent.parent / "data" / "insurance_catalog.json"))
os.environ.setdefault("DEALS_PATH", str(Path(__file__).parent.parent / "data" / "mock_deals.json"))
os.environ.setdefault("USERS_PATH", str(Path(__file__).parent.parent / "data" / "mock_users.json"))
os.environ.setdefault("AB_DB_PATH", str(Path(__file__).parent.parent / "data" / "test_ab_events.db"))


@pytest.fixture
def sample_deal():
    """Sample single deal for testing."""
    return {
        "deal_id": "TEST001",
        "merchant": "IndiGo",
        "category": "travel",
        "subcategory": "flight",
        "deal_value": 12400,
        "user_history": {
            "risk_tier": "medium",
            "total_purchases": 18,
            "categories_bought": ["travel", "electronics"],
        },
    }


@pytest.fixture
def sample_multi_cart_deal():
    """Sample multi-cart deal for testing."""
    return {
        "deal_id": "TEST_MULTI",
        "merchant": "CART:Myntra+MakeMyTrip",
        "category": "MULTI",
        "subcategory": "MULTI",
        "deal_value": 11400,
        "cart_items": [
            {"merchant": "Myntra", "category": "fashion", "subcategory": "apparel", "deal_value": 1800},
            {"merchant": "MakeMyTrip", "category": "travel", "subcategory": "flight", "deal_value": 9600},
        ],
        "user_history": {
            "risk_tier": "medium",
            "total_purchases": 14,
            "categories_bought": ["fashion", "travel"],
        },
    }


@pytest.fixture
def low_value_deal():
    """Deal below threshold for testing."""
    return {
        "deal_id": "TEST_LOW",
        "merchant": "SmallShop",
        "category": "fashion",
        "subcategory": "accessory",
        "deal_value": 150,
        "user_history": {"risk_tier": "medium"},
    }


@pytest.fixture(autouse=True)
async def cleanup_test_db():
    """Clean up test database after each test."""
    yield
    # Clean up test DB
    test_db = Path(__file__).parent.parent / "data" / "test_ab_events.db"
    if test_db.exists():
        try:
            test_db.unlink()
        except Exception:
            pass
