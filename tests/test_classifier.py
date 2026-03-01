"""Tests for the insurance classifier engine."""

import pytest
from insurance_engine.classifier import classify_intent, _apply_rules


class TestClassifier:
    """Test the classification engine."""

    @pytest.mark.asyncio
    async def test_travel_flight_high_value(self):
        """Test travel flight with high value gets TRVL_MED."""
        result = await classify_intent(
            merchant="IndiGo",
            category="travel",
            subcategory="flight",
            deal_value=12400,
        )
        product_ids = [p.product_id for p in result.top_products]
        assert "TRVL_CANCEL" in product_ids
        assert "TRVL_MED" in product_ids  # deal_value > 8000

    @pytest.mark.asyncio
    async def test_travel_flight_low_value(self):
        """Test travel flight with low value doesn't get TRVL_MED."""
        result = await classify_intent(
            merchant="IndiGo",
            category="travel",
            subcategory="flight",
            deal_value=5000,
        )
        product_ids = [p.product_id for p in result.top_products]
        assert "TRVL_CANCEL" in product_ids
        assert "TRVL_MED" not in product_ids  # deal_value <= 8000

    @pytest.mark.asyncio
    async def test_travel_hotel(self):
        """Test travel hotel classification."""
        result = await classify_intent(
            merchant="MakeMyTrip",
            category="travel",
            subcategory="hotel",
            deal_value=8500,
        )
        product_ids = [p.product_id for p in result.top_products]
        assert "TRVL_RETURN" in product_ids

    @pytest.mark.asyncio
    async def test_electronics_gadget(self):
        """Test electronics gadget classification."""
        result = await classify_intent(
            merchant="Boat",
            category="electronics",
            subcategory="gadget",
            deal_value=2999,
        )
        product_ids = [p.product_id for p in result.top_products]
        assert "ELEC_WARRANTY" in product_ids

    @pytest.mark.asyncio
    async def test_health_pharmacy(self):
        """Test health pharmacy classification."""
        result = await classify_intent(
            merchant="Nykaa",
            category="health",
            subcategory="pharmacy",
            deal_value=499,
        )
        product_ids = [p.product_id for p in result.top_products]
        assert "HEALTH_OPD" in product_ids

    @pytest.mark.asyncio
    async def test_food_delivery(self):
        """Test food delivery classification."""
        result = await classify_intent(
            merchant="Swiggy",
            category="food",
            subcategory="delivery",
            deal_value=500,
        )
        product_ids = [p.product_id for p in result.top_products]
        assert "FOOD_ACCIDENT" in product_ids

    @pytest.mark.asyncio
    async def test_multi_cart_context(self):
        """Test multi-cart context detection."""
        result = await classify_intent(
            merchant="CART:Store1+Store2",
            category="MULTI",
            subcategory="MULTI",
            deal_value=10000,
        )
        assert result.cart_context == "multi"

    @pytest.mark.asyncio
    async def test_max_two_products(self):
        """Test that max 2 products are returned."""
        result = await classify_intent(
            merchant="AirAsia",
            category="travel",
            subcategory="international",
            deal_value=50000,
        )
        assert len(result.top_products) <= 2


class TestApplyRules:
    """Test the rule application function."""

    def test_exact_match_priority(self):
        """Test that exact matches are prioritized."""
        matches = _apply_rules("travel", "flight", 10000)
        assert len(matches) > 0
        assert matches[0].product_id == "TRVL_CANCEL"

    def test_category_fallback(self):
        """Test category-level fallback for unknown subcategory."""
        matches = _apply_rules("travel", "unknown", 10000)
        assert len(matches) > 0

    def test_wildcard_subcategory(self):
        """Test wildcard subcategory matching."""
        matches = _apply_rules("fashion", "anything", 5000)
        assert len(matches) > 0
        assert matches[0].product_id == "PURCHASE_PROTECT"

    def test_empty_for_unknown_category(self):
        """Test empty result for completely unknown category."""
        matches = _apply_rules("automotive", "cars", 10000)
        assert len(matches) == 0
