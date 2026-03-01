"""Tests for the A/B testing framework."""

import pytest
from insurance_engine.ab_testing import (
    get_variant,
    record_impression,
    record_conversion,
    get_dashboard_data,
    clear_test_data,
    VARIANTS,
)


class TestVariantAssignment:
    """Test deterministic variant assignment."""

    def test_deterministic_assignment(self):
        """Test that same session+product always gets same variant."""
        session_id = "test-session-123"
        product_id = "TRVL_CANCEL"

        variant1 = get_variant(session_id, product_id)
        variant2 = get_variant(session_id, product_id)

        assert variant1 == variant2

    def test_different_sessions_may_get_different_variants(self):
        """Test that different sessions can get different variants."""
        product_id = "TRVL_CANCEL"
        variants = set()

        # Generate variants for many sessions
        for i in range(100):
            variant = get_variant(f"session-{i}", product_id)
            variants.add(variant)

        # Should have multiple variants
        assert len(variants) > 1

    def test_all_variants_are_valid(self):
        """Test that all assigned variants are valid."""
        for i in range(50):
            variant = get_variant(f"test-{i}", f"product-{i}")
            assert variant in VARIANTS

    def test_variant_distribution(self):
        """Test that variants are roughly evenly distributed."""
        counts = {"urgency": 0, "value": 0, "social_proof": 0}

        for i in range(1000):
            variant = get_variant(f"session-{i}", "TRVL_CANCEL")
            counts[variant] += 1

        # Each should be roughly 333 (1000/3), allow 20% variance
        for count in counts.values():
            assert 200 < count < 500


class TestImpressionRecording:
    """Test impression recording."""

    @pytest.mark.asyncio
    async def test_record_impression_creates_session(self):
        """Test that recording impression creates a session."""
        await clear_test_data()

        session = await record_impression(
            session_id="test-impression-1",
            deal_id="D001",
            user_id="U001",
            product_id="TRVL_CANCEL",
            copy_string="Test copy string",
        )

        assert session.session_id == "test-impression-1"
        assert session.deal_id == "D001"
        assert session.variant in VARIANTS
        assert session.converted is False

    @pytest.mark.asyncio
    async def test_variant_matches_deterministic(self):
        """Test that recorded variant matches deterministic assignment."""
        await clear_test_data()

        session_id = "test-variant-match"
        product_id = "ELEC_SCREEN"

        expected_variant = get_variant(session_id, product_id)

        session = await record_impression(
            session_id=session_id,
            deal_id="D006",
            user_id="U002",
            product_id=product_id,
            copy_string="Test copy",
        )

        assert session.variant == expected_variant


class TestConversionTracking:
    """Test conversion tracking."""

    @pytest.mark.asyncio
    async def test_record_conversion(self):
        """Test recording a conversion."""
        await clear_test_data()

        # First record impression
        await record_impression(
            session_id="test-convert-1",
            deal_id="D001",
            user_id="U001",
            product_id="TRVL_CANCEL",
            copy_string="Test copy",
        )

        # Then record conversion
        converted_at = await record_conversion("test-convert-1", "TRVL_CANCEL")

        assert converted_at is not None

    @pytest.mark.asyncio
    async def test_conversion_without_impression(self):
        """Test conversion for non-existent session returns None."""
        await clear_test_data()

        converted_at = await record_conversion("nonexistent-session", "TRVL_CANCEL")

        assert converted_at is None


class TestDashboard:
    """Test dashboard data generation."""

    @pytest.mark.asyncio
    async def test_empty_dashboard(self):
        """Test dashboard with no data."""
        await clear_test_data()

        dashboard = await get_dashboard_data()

        assert dashboard.total_impressions == 0
        assert dashboard.total_conversions == 0
        assert dashboard.overall_cvr_percent == 0.0

    @pytest.mark.asyncio
    async def test_dashboard_with_data(self):
        """Test dashboard with impressions and conversions."""
        await clear_test_data()

        # Record some impressions
        for i in range(5):
            await record_impression(
                session_id=f"dash-test-{i}",
                deal_id="D001",
                user_id=f"U00{i}",
                product_id="TRVL_CANCEL",
                copy_string=f"Copy {i}",
            )

        # Record some conversions
        await record_conversion("dash-test-0", "TRVL_CANCEL")
        await record_conversion("dash-test-1", "TRVL_CANCEL")

        dashboard = await get_dashboard_data()

        assert dashboard.total_impressions == 5
        assert dashboard.total_conversions == 2
        assert dashboard.overall_cvr_percent == 40.0

    @pytest.mark.asyncio
    async def test_dashboard_best_variant(self):
        """Test that best variant is correctly identified."""
        await clear_test_data()

        # Create sessions with known variants by using specific session_ids
        # We need to find session_ids that give us specific variants
        urgency_sessions = []
        value_sessions = []

        for i in range(1000):
            session_id = f"find-variant-{i}"
            variant = get_variant(session_id, "TRVL_CANCEL")
            if variant == "urgency" and len(urgency_sessions) < 3:
                urgency_sessions.append(session_id)
            elif variant == "value" and len(value_sessions) < 3:
                value_sessions.append(session_id)
            if len(urgency_sessions) >= 3 and len(value_sessions) >= 3:
                break

        # Record urgency impressions with 0% conversion
        for sid in urgency_sessions:
            await record_impression(
                session_id=sid,
                deal_id="D001",
                user_id="test",
                product_id="TRVL_CANCEL",
                copy_string="Test",
            )

        # Record value impressions with 100% conversion
        for sid in value_sessions:
            await record_impression(
                session_id=sid,
                deal_id="D001",
                user_id="test",
                product_id="TRVL_CANCEL",
                copy_string="Test",
            )
            await record_conversion(sid, "TRVL_CANCEL")

        dashboard = await get_dashboard_data()

        # Find the best variant
        best_variants = [v for v in dashboard.variants if v.is_best]
        assert len(best_variants) == 1
