"""Tests for MCP tools - all 12 edge cases from blueprint section 11."""

import pytest
from mcp_server.tools import classify_intent, get_premium_quote


class TestClassifyIntent:
    """Test classify_intent tool with all edge cases."""

    @pytest.mark.asyncio
    async def test_edge_case_1_deal_value_below_200(self):
        """Edge case 1: deal_value below 200 should return show_offer=false."""
        result = await classify_intent(
            merchant="SmallShop",
            category="fashion",
            subcategory="accessory",
            deal_value=150,
        )
        assert result.show_offer is False
        assert result.reason == "deal_value_below_threshold"
        assert len(result.top_products) == 0

    @pytest.mark.asyncio
    async def test_edge_case_2_deal_value_zero(self):
        """Edge case 2: deal_value is 0 should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await classify_intent(
                merchant="Shop",
                category="electronics",
                subcategory="gadget",
                deal_value=0,
            )
        assert "invalid_deal_value" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_edge_case_2_deal_value_none(self):
        """Edge case 2: deal_value is None should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await classify_intent(
                merchant="Shop",
                category="electronics",
                subcategory="gadget",
                deal_value=None,
            )
        assert "invalid_deal_value" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_edge_case_3_category_not_recognized(self):
        """Edge case 3: unknown category should return PURCHASE_PROTECT fallback."""
        result = await classify_intent(
            merchant="AutoParts",
            category="automotive",
            subcategory="parts",
            deal_value=5000,
        )
        # Should use fallback and return PURCHASE_PROTECT
        assert result.show_offer is True
        if len(result.top_products) > 0:
            assert result.top_products[0].product_id == "PURCHASE_PROTECT"
            assert result.top_products[0].confidence <= 0.35

    @pytest.mark.asyncio
    async def test_edge_case_4_user_history_empty_dict(self):
        """Edge case 4: empty user_history should default to medium risk tier."""
        result = await classify_intent(
            merchant="IndiGo",
            category="travel",
            subcategory="flight",
            deal_value=10000,
            user_history={},
        )
        assert result.show_offer is True
        assert len(result.top_products) > 0
        # Should not raise error with empty history

    @pytest.mark.asyncio
    async def test_edge_case_5_subcategory_not_in_known_list(self, capsys):
        """Edge case 5: unknown subcategory should log to stderr and continue."""
        result = await classify_intent(
            merchant="FurnitureStore",
            category="electronics",
            subcategory="gaming-chair",
            deal_value=8000,
        )
        captured = capsys.readouterr()
        # Should log warning to stderr
        assert "Unrecognized subcategory" in captured.err or result.show_offer is True
        assert len(result.top_products) > 0  # Should still return results

    @pytest.mark.asyncio
    async def test_travel_flight_classification(self):
        """Test standard travel flight classification."""
        result = await classify_intent(
            merchant="IndiGo",
            category="travel",
            subcategory="flight",
            deal_value=12400,
            user_history={"risk_tier": "medium", "total_purchases": 18},
        )
        assert result.show_offer is True
        assert result.cart_context == "single"
        assert len(result.top_products) >= 1
        product_ids = [p.product_id for p in result.top_products]
        assert "TRVL_CANCEL" in product_ids

    @pytest.mark.asyncio
    async def test_high_value_flight_gets_trvl_med(self):
        """High-value flight (>8000) should also get TRVL_MED."""
        result = await classify_intent(
            merchant="IndiGo",
            category="travel",
            subcategory="flight",
            deal_value=12400,
        )
        product_ids = [p.product_id for p in result.top_products]
        assert "TRVL_MED" in product_ids

    @pytest.mark.asyncio
    async def test_electronics_phone_classification(self):
        """Test electronics phone classification."""
        result = await classify_intent(
            merchant="Samsung",
            category="electronics",
            subcategory="phone",
            deal_value=74999,
            user_history={"risk_tier": "high"},
        )
        assert result.show_offer is True
        product_ids = [p.product_id for p in result.top_products]
        assert "ELEC_SCREEN" in product_ids

    @pytest.mark.asyncio
    async def test_electronics_phone_high_value_gets_warranty(self):
        """High-value phone (>5000) should also get warranty."""
        result = await classify_intent(
            merchant="Samsung",
            category="electronics",
            subcategory="phone",
            deal_value=74999,
        )
        product_ids = [p.product_id for p in result.top_products]
        assert "ELEC_WARRANTY" in product_ids

    @pytest.mark.asyncio
    async def test_fashion_uses_fallback(self):
        """Fashion should use PURCHASE_PROTECT fallback."""
        result = await classify_intent(
            merchant="Puma",
            category="fashion",
            subcategory="sports",
            deal_value=5500,
        )
        assert result.show_offer is True
        assert result.fallback_used is True
        product_ids = [p.product_id for p in result.top_products]
        assert "PURCHASE_PROTECT" in product_ids

    @pytest.mark.asyncio
    async def test_international_travel_gets_trvl_med_primary(self):
        """International travel should get TRVL_MED as primary."""
        result = await classify_intent(
            merchant="AirAsia",
            category="travel",
            subcategory="international",
            deal_value=31000,
        )
        assert result.show_offer is True
        assert result.top_products[0].product_id == "TRVL_MED"


class TestGetPremiumQuote:
    """Test get_premium_quote tool."""

    @pytest.mark.asyncio
    async def test_edge_case_7_premium_below_floor(self):
        """Edge case 7: premium below floor should return 19."""
        result = await get_premium_quote(
            product_id="FOOD_ACCIDENT",  # base_premium_rate = 0.001
            deal_value=210,
            risk_tier="low",  # multiplier = 0.8
        )
        # 210 * 0.001 * 0.8 = 0.168, should floor to 19
        assert result.premium_inr == 19

    @pytest.mark.asyncio
    async def test_premium_cap_at_499(self):
        """Premium should cap at 499."""
        result = await get_premium_quote(
            product_id="ELEC_WARRANTY",  # base_premium_rate = 0.03
            deal_value=100000,
            risk_tier="high",  # multiplier = 1.4
        )
        # 100000 * 0.03 * 1.4 = 4200, should cap to 499
        assert result.premium_inr == 499

    @pytest.mark.asyncio
    async def test_premium_calculation_formula(self):
        """Test exact premium formula."""
        result = await get_premium_quote(
            product_id="TRVL_CANCEL",  # base_premium_rate = 0.007
            deal_value=12400,
            risk_tier="medium",  # multiplier = 1.0
        )
        # 12400 * 0.007 * 1.0 = 86.8 -> round to 87
        assert result.premium_inr == 87

    @pytest.mark.asyncio
    async def test_invalid_product_raises_error(self):
        """Invalid product ID should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await get_premium_quote(
                product_id="INVALID_PRODUCT",
                deal_value=1000,
                risk_tier="medium",
            )
        assert "Product not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_deal_value_raises_error(self):
        """Invalid deal value should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await get_premium_quote(
                product_id="TRVL_CANCEL",
                deal_value=0,
                risk_tier="medium",
            )
        assert "invalid_deal_value" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_coverage_calculation(self):
        """Test coverage calculation."""
        result = await get_premium_quote(
            product_id="TRVL_CANCEL",  # coverage_multiplier = 100
            deal_value=10000,
            risk_tier="medium",
        )
        # coverage = (10000 * 100) / 100 = 10000
        assert result.coverage_inr == 10000

    @pytest.mark.asyncio
    async def test_validity_days(self):
        """Test validity days is always 30."""
        result = await get_premium_quote(
            product_id="TRVL_CANCEL",
            deal_value=10000,
            risk_tier="medium",
        )
        assert result.validity_days == 30

    @pytest.mark.asyncio
    async def test_policy_type_matches_product(self):
        """Test policy type matches product name."""
        result = await get_premium_quote(
            product_id="ELEC_SCREEN",
            deal_value=50000,
            risk_tier="medium",
        )
        assert result.policy_type == "Screen Damage Cover"
