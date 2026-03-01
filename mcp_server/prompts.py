"""MCP Prompts for GrabInsurance.

Contains the generate_insurance_copy_prompt with all 4 good/bad few-shot
examples from blueprint section 12. Variant type changes the framing
instruction, not just a label.
"""

from typing import Literal


def generate_insurance_copy_prompt(
    product_name: str,
    deal_description: str,
    premium_inr: float,
    variant: Literal["urgency", "value", "social_proof"],
) -> list[dict]:
    """Generate a prompt for creating personalized insurance copy.

    This prompt instructs Claude to generate one copy string under 120 characters
    that mentions both the deal amount and premium explicitly. The variant type
    changes the actual framing instruction, not just a label.

    Args:
        product_name: Name of the insurance product
        deal_description: Description including merchant, destination, amount
        premium_inr: Premium amount in INR
        variant: A/B variant type affecting copy framing

    Returns:
        Message list (user role) for Claude API
    """
    # Variant-specific framing instructions
    variant_instructions = {
        "urgency": """FRAMING: Use time pressure, scarcity, or loss aversion.
Examples of urgency framing:
- "Only valid for the next 2 hours"
- "What if your flight gets cancelled tomorrow?"
- "Once you leave this page, offer expires"
- Use words like: "now", "today", "before", "last chance", "don't risk"
""",
        "value": """FRAMING: Use coverage ratio math and value proposition.
Examples of value framing:
- "Your Rs X premium buys Rs Y protection"
- "140x coverage on your premium"
- "Less than a coffee protects your entire purchase"
- Use numbers and ratios prominently
""",
        "social_proof": """FRAMING: Mention how many users protected similar deals.
Examples of social proof framing:
- "4,200 travelers protected similar trips last month"
- "Join 10,000+ GrabOn users who secured their electronics"
- "Most popular protection for Samsung buyers"
- Use specific numbers and peer behavior
""",
    }

    prompt = f"""You are a copywriter for GrabInsurance. Generate ONE insurance offer copy string.

PRODUCT: {product_name}
DEAL: {deal_description}
PREMIUM: Rs {premium_inr:.0f}

{variant_instructions[variant]}

HARD RULES - MUST FOLLOW:
1. Always mention the deal amount in INR explicitly (e.g., "your Rs 12,400 Goa trip")
2. Always mention the premium in INR explicitly (e.g., "for Rs 89")
3. Maximum 120 characters total
4. NEVER use these words: "Buy", "Purchase", "Get protected", "Insurance available"
5. When merchant name is known, include destination or product name
6. All copy must be in English only

FEW-SHOT EXAMPLES:

BAD: "Buy Travel Insurance for your trip"
GOOD: "Your Rs 12,400 Goa flight. Cancel for any reason. Cover for Rs 89."

BAD: "Electronics warranty available"
GOOD: "Rs 74,999 Samsung S24. One crack = Rs 18,000 repair. Cover for Rs 499."

BAD: "Health cover for your purchase"
GOOD: "Healthkart order protected 30 days. Theft, damage, non-delivery. Rs 31."

BAD: "Personal accident insurance"
GOOD: "Swiggy delivery order? Rs 19 covers accidental harm during your meal."

Now generate ONE copy string that follows all rules and uses the {variant.upper()} framing.
Return ONLY the copy string, nothing else."""

    return [{"role": "user", "content": prompt}]


def get_copy_system_message() -> str:
    """Return the system message for copy generation.

    Returns:
        System message string for Claude
    """
    return """You are an expert insurance copywriter for GrabInsurance, India's leading contextual insurance platform.

Your copy is:
- Specific: mentions exact amounts, merchants, destinations
- Concise: under 120 characters
- Action-oriented: creates urgency without hard-sell language
- Compliant: never uses "Buy", "Purchase", or generic phrases

You understand Indian consumers and write copy that resonates with deal-seekers."""
