"""Tests for the pricing engine."""

import pytest
from insurance_engine.pricing import calculate_premium, PREMIUM_FLOOR, PREMIUM_CAP, RISK_MULTIPLIERS


class TestPricingEngine:
    """Test the pricing calculation engine."""

    def test_premium_floor(self):
        """Test that premium never goes below floor."""
        quote = calculate_premium(
            product_id="FOOD_ACCIDENT",  # 0.001 rate
            deal_value=200,
            risk_tier="low",  # 0.8 multiplier
        )
        # 200 * 0.001 * 0.8 = 0.16, should floor to 19
        assert quote.premium_inr == PREMIUM_FLOOR
        assert quote.premium_inr == 19

    def test_premium_cap(self):
        """Test that premium never exceeds cap."""
        quote = calculate_premium(
            product_id="ELEC_WARRANTY",  # 0.03 rate
            deal_value=50000,
            risk_tier="high",  # 1.4 multiplier
        )
        # 50000 * 0.03 * 1.4 = 2100, should cap to 499
        assert quote.premium_inr == PREMIUM_CAP
        assert quote.premium_inr == 499

    def test_low_risk_multiplier(self):
        """Test low risk tier multiplier."""
        quote = calculate_premium(
            product_id="TRVL_CANCEL",  # 0.007 rate
            deal_value=10000,
            risk_tier="low",  # 0.8 multiplier
        )
        # 10000 * 0.007 * 0.8 = 56
        assert quote.premium_inr == 56

    def test_medium_risk_multiplier(self):
        """Test medium risk tier multiplier."""
        quote = calculate_premium(
            product_id="TRVL_CANCEL",  # 0.007 rate
            deal_value=10000,
            risk_tier="medium",  # 1.0 multiplier
        )
        # 10000 * 0.007 * 1.0 = 70
        assert quote.premium_inr == 70

    def test_high_risk_multiplier(self):
        """Test high risk tier multiplier."""
        quote = calculate_premium(
            product_id="TRVL_CANCEL",  # 0.007 rate
            deal_value=10000,
            risk_tier="high",  # 1.4 multiplier
        )
        # 10000 * 0.007 * 1.4 = 98
        assert quote.premium_inr == 98

    def test_invalid_risk_tier_defaults_to_medium(self):
        """Test that invalid risk tier defaults to medium."""
        quote = calculate_premium(
            product_id="TRVL_CANCEL",
            deal_value=10000,
            risk_tier="invalid",
        )
        expected = calculate_premium(
            product_id="TRVL_CANCEL",
            deal_value=10000,
            risk_tier="medium",
        )
        assert quote.premium_inr == expected.premium_inr

    def test_coverage_calculation(self):
        """Test coverage calculation from multiplier."""
        quote = calculate_premium(
            product_id="TRVL_MED",  # coverage_multiplier = 200
            deal_value=10000,
            risk_tier="medium",
        )
        # coverage = (10000 * 200) / 100 = 20000
        assert quote.coverage_inr == 20000

    def test_validity_always_30_days(self):
        """Test that validity is always 30 days."""
        for product_id in ["TRVL_CANCEL", "ELEC_SCREEN", "HEALTH_OPD"]:
            quote = calculate_premium(product_id, 10000, "medium")
            assert quote.validity_days == 30

    def test_invalid_product_raises_error(self):
        """Test that invalid product ID raises error."""
        with pytest.raises(ValueError) as exc_info:
            calculate_premium("INVALID", 10000, "medium")
        assert "Product not found" in str(exc_info.value)

    def test_zero_deal_value_raises_error(self):
        """Test that zero deal value raises error."""
        with pytest.raises(ValueError) as exc_info:
            calculate_premium("TRVL_CANCEL", 0, "medium")
        assert "invalid_deal_value" in str(exc_info.value)

    def test_negative_deal_value_raises_error(self):
        """Test that negative deal value raises error."""
        with pytest.raises(ValueError) as exc_info:
            calculate_premium("TRVL_CANCEL", -100, "medium")
        assert "invalid_deal_value" in str(exc_info.value)


class TestRiskMultipliers:
    """Test risk multiplier values."""

    def test_multiplier_values(self):
        """Test that multipliers match blueprint."""
        assert RISK_MULTIPLIERS["low"] == 0.8
        assert RISK_MULTIPLIERS["medium"] == 1.0
        assert RISK_MULTIPLIERS["high"] == 1.4

    def test_bounds(self):
        """Test floor and cap values match blueprint."""
        assert PREMIUM_FLOOR == 19
        assert PREMIUM_CAP == 499
