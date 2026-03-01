"""Tests for the multi-category cart resolver."""

import pytest
from mcp_server.schemas import CartItem, DealObject, UserHistory
from insurance_engine.cart_resolver import resolve_multi_cart, classify_deal_with_cart


class TestCartResolver:
    """Test the cart resolution waterfall."""

    @pytest.mark.asyncio
    async def test_travel_always_wins(self):
        """Test that travel always takes primary slot in multi-cart."""
        cart_items = [
            CartItem(merchant="Myntra", category="fashion", subcategory="apparel", deal_value=1800),
            CartItem(merchant="MakeMyTrip", category="travel", subcategory="flight", deal_value=9600),
        ]

        result = await resolve_multi_cart(cart_items, 11400)

        assert result.show_offer is True
        assert result.cart_context == "multi"
        assert len(result.top_products) >= 1
        assert result.top_products[0].product_id == "TRVL_CANCEL"

    @pytest.mark.asyncio
    async def test_electronics_above_5000_gets_second_slot(self):
        """Test that electronics >5000 gets secondary slot."""
        cart_items = [
            CartItem(merchant="IndiGo", category="travel", subcategory="flight", deal_value=15000),
            CartItem(merchant="Samsung", category="electronics", subcategory="phone", deal_value=70000),
        ]

        result = await resolve_multi_cart(cart_items, 85000)

        assert len(result.top_products) == 2
        product_ids = [p.product_id for p in result.top_products]
        # Travel should be first
        assert result.top_products[0].product_id in ["TRVL_CANCEL", "TRVL_MED"]
        # Electronics should be present
        assert any(pid in product_ids for pid in ["ELEC_SCREEN", "ELEC_WARRANTY"])

    @pytest.mark.asyncio
    async def test_food_health_higher_value_wins(self):
        """Test that higher value item wins when no travel/electronics."""
        cart_items = [
            CartItem(merchant="Swiggy", category="food", subcategory="delivery", deal_value=400),
            CartItem(merchant="Healthkart", category="health", subcategory="supplement", deal_value=2100),
        ]

        result = await resolve_multi_cart(cart_items, 2500)

        assert result.show_offer is True
        # Health has higher value, should get HEALTH_OPD
        product_ids = [p.product_id for p in result.top_products]
        assert "HEALTH_OPD" in product_ids

    @pytest.mark.asyncio
    async def test_never_more_than_two_products(self):
        """Test that max 2 products are returned regardless of cart size."""
        cart_items = [
            CartItem(merchant="IndiGo", category="travel", subcategory="flight", deal_value=10000),
            CartItem(merchant="Samsung", category="electronics", subcategory="phone", deal_value=50000),
            CartItem(merchant="Healthkart", category="health", subcategory="pharmacy", deal_value=2000),
            CartItem(merchant="Zomato", category="food", subcategory="delivery", deal_value=500),
        ]

        result = await resolve_multi_cart(cart_items, 62500)

        assert len(result.top_products) <= 2

    @pytest.mark.asyncio
    async def test_edge_case_6_duplicate_category(self):
        """Test deduplication when same category appears twice."""
        cart_items = [
            CartItem(merchant="IndiGo", category="travel", subcategory="flight", deal_value=5000),
            CartItem(merchant="MakeMyTrip", category="travel", subcategory="flight", deal_value=15000),
        ]

        result = await resolve_multi_cart(cart_items, 20000)

        # Should use the higher value travel item (15000)
        assert result.show_offer is True
        # Should get TRVL_MED for >8000 value
        product_ids = [p.product_id for p in result.top_products]
        assert "TRVL_MED" in product_ids

    @pytest.mark.asyncio
    async def test_deal_value_below_threshold(self):
        """Test that low deal value returns no offer."""
        cart_items = [
            CartItem(merchant="Shop1", category="fashion", subcategory="item", deal_value=50),
            CartItem(merchant="Shop2", category="food", subcategory="snack", deal_value=50),
        ]

        result = await resolve_multi_cart(cart_items, 100)

        assert result.show_offer is False

    @pytest.mark.asyncio
    async def test_empty_cart(self):
        """Test empty cart returns no offer."""
        result = await resolve_multi_cart([], 1000)

        assert result.show_offer is False


class TestClassifyDealWithCart:
    """Test the combined classification function."""

    @pytest.mark.asyncio
    async def test_single_deal_uses_classifier(self):
        """Test that single deal (no cart_items) uses regular classifier."""
        deal = DealObject(
            merchant="IndiGo",
            category="travel",
            subcategory="flight",
            deal_value=12400,
            user_history=UserHistory(risk_tier="medium"),
        )

        result = await classify_deal_with_cart(deal)

        assert result.cart_context == "single"
        product_ids = [p.product_id for p in result.top_products]
        assert "TRVL_CANCEL" in product_ids

    @pytest.mark.asyncio
    async def test_multi_cart_uses_resolver(self):
        """Test that multi-cart deal uses cart resolver."""
        deal = DealObject(
            merchant="CART:Myntra+MakeMyTrip",
            category="MULTI",
            subcategory="MULTI",
            deal_value=11400,
            user_history=UserHistory(risk_tier="medium"),
            cart_items=[
                CartItem(merchant="Myntra", category="fashion", subcategory="apparel", deal_value=1800),
                CartItem(merchant="MakeMyTrip", category="travel", subcategory="flight", deal_value=9600),
            ],
        )

        result = await classify_deal_with_cart(deal)

        assert result.cart_context == "multi"
        # Travel should win
        assert result.top_products[0].product_id == "TRVL_CANCEL"
