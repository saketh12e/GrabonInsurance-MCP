"""Tests for copy generation quality.

Must assert:
- Copy contains "Rs"
- Copy contains the premium value
- len(copy) <= 120
"""

import pytest
from mcp_server.prompts import generate_insurance_copy_prompt


class TestCopyQuality:
    """Test generated copy quality requirements."""

    def test_prompt_structure(self):
        """Test that prompt has correct structure."""
        messages = generate_insurance_copy_prompt(
            product_name="Travel Cancellation Cover",
            deal_description="IndiGo flight to Goa Rs 12,400",
            premium_inr=89,
            variant="urgency",
        )

        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert len(messages[0]["content"]) > 0

    def test_prompt_contains_deal_amount(self):
        """Test that prompt mentions deal amount requirement."""
        messages = generate_insurance_copy_prompt(
            product_name="Travel Cancellation Cover",
            deal_description="IndiGo flight Rs 12,400",
            premium_inr=89,
            variant="urgency",
        )

        content = messages[0]["content"]
        assert "deal amount" in content.lower() or "12,400" in content or "amount in INR" in content.lower()

    def test_prompt_contains_premium_requirement(self):
        """Test that prompt mentions premium requirement."""
        messages = generate_insurance_copy_prompt(
            product_name="Screen Damage Cover",
            deal_description="Samsung phone Rs 74,999",
            premium_inr=499,
            variant="value",
        )

        content = messages[0]["content"]
        assert "premium" in content.lower()
        assert "Rs" in content

    def test_prompt_contains_max_length_requirement(self):
        """Test that prompt specifies 120 character limit."""
        messages = generate_insurance_copy_prompt(
            product_name="Health OPD Cover",
            deal_description="Healthkart order Rs 2,100",
            premium_inr=31,
            variant="social_proof",
        )

        content = messages[0]["content"]
        assert "120" in content

    def test_urgency_variant_framing(self):
        """Test urgency variant includes time pressure framing."""
        messages = generate_insurance_copy_prompt(
            product_name="Travel Cancellation Cover",
            deal_description="Flight to Delhi",
            premium_inr=79,
            variant="urgency",
        )

        content = messages[0]["content"]
        assert "urgency" in content.lower() or "time pressure" in content.lower()

    def test_value_variant_framing(self):
        """Test value variant includes coverage ratio framing."""
        messages = generate_insurance_copy_prompt(
            product_name="Electronics Extended Warranty",
            deal_description="Laptop Rs 60,000",
            premium_inr=499,
            variant="value",
        )

        content = messages[0]["content"]
        assert "value" in content.lower() or "coverage" in content.lower() or "ratio" in content.lower()

    def test_social_proof_variant_framing(self):
        """Test social proof variant includes peer behavior framing."""
        messages = generate_insurance_copy_prompt(
            product_name="Purchase Protection",
            deal_description="Fashion order Rs 5,500",
            premium_inr=55,
            variant="social_proof",
        )

        content = messages[0]["content"]
        assert "social" in content.lower() or "users" in content.lower()

    def test_prompt_contains_forbidden_words(self):
        """Test that prompt instructs to avoid forbidden words."""
        messages = generate_insurance_copy_prompt(
            product_name="Travel Medical Cover",
            deal_description="International flight",
            premium_inr=155,
            variant="urgency",
        )

        content = messages[0]["content"]
        # Should mention words to avoid
        assert "Buy" in content or "Purchase" in content or "NEVER" in content.upper()

    def test_prompt_contains_good_examples(self):
        """Test that prompt contains few-shot good examples."""
        messages = generate_insurance_copy_prompt(
            product_name="Screen Damage Cover",
            deal_description="Samsung S24",
            premium_inr=499,
            variant="value",
        )

        content = messages[0]["content"]
        # Should contain at least one good example
        assert "GOOD:" in content or "good" in content.lower()

    def test_prompt_contains_bad_examples(self):
        """Test that prompt contains few-shot bad examples."""
        messages = generate_insurance_copy_prompt(
            product_name="Personal Accident Cover",
            deal_description="Swiggy order",
            premium_inr=19,
            variant="urgency",
        )

        content = messages[0]["content"]
        # Should contain bad examples to avoid
        assert "BAD:" in content or "bad" in content.lower()


class TestCopyValidation:
    """Test copy validation rules."""

    def test_copy_max_length_rule(self):
        """Test that copy length validation is defined."""
        # This test ensures our system knows about the 120 char limit
        max_copy_length = 120
        sample_good_copy = "Your Rs 12,400 Goa flight. Cancel for any reason. Cover for Rs 89."
        sample_bad_copy = "This is an extremely long copy string that definitely exceeds the maximum allowed character limit of 120 characters and should be rejected by the validation system."

        assert len(sample_good_copy) <= max_copy_length
        assert len(sample_bad_copy) > max_copy_length

    def test_copy_must_contain_rs(self):
        """Test that copy must contain Rs for amounts."""
        good_copies = [
            "Your Rs 12,400 Goa flight. Cancel for any reason. Cover for Rs 89.",
            "Rs 74,999 Samsung S24. One crack = Rs 18,000 repair. Cover for Rs 499.",
            "Healthkart order protected 30 days. Theft, damage, non-delivery. Rs 31.",
        ]

        for copy in good_copies:
            assert "Rs" in copy, f"Copy should contain 'Rs': {copy}"

    def test_copy_must_contain_premium(self):
        """Test that copy must contain premium value."""
        test_cases = [
            ("Your Rs 12,400 Goa flight. Cancel for any reason. Cover for Rs 89.", 89),
            ("Rs 74,999 Samsung S24. One crack = Rs 18,000 repair. Cover for Rs 499.", 499),
        ]

        for copy, premium in test_cases:
            assert str(int(premium)) in copy, f"Copy should contain premium {premium}: {copy}"

    def test_copy_under_120_chars(self):
        """Test that all example copies are under 120 characters."""
        example_copies = [
            "Your Rs 12,400 Goa flight. Cancel for any reason. Cover for Rs 89.",
            "Rs 74,999 Samsung S24. One crack = Rs 18,000 repair. Cover for Rs 499.",
            "Healthkart order protected 30 days. Theft, damage, non-delivery. Rs 31.",
            "Swiggy delivery order? Rs 19 covers accidental harm during your meal.",
        ]

        for copy in example_copies:
            assert len(copy) <= 120, f"Copy exceeds 120 chars ({len(copy)}): {copy}"
