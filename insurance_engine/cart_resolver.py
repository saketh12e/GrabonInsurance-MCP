"""Multi-Category Cart Resolution Logic.

Applies the exact waterfall from blueprint section 10:
1. If travel exists → travel insurance takes primary slot
2. If electronics > Rs 5000 → electronics cover takes second slot
3. If no travel and no qualifying electronics → top 2 by confidence
4. If 3+ categories and no clear winner → top 2 by confidence
5. Never return more than 2 products
"""

from mcp_server.schemas import CartItem, ClassificationResult, DealObject, InsuranceMatch
from insurance_engine.catalog import lookup_by_id
from insurance_engine.classifier import _apply_rules


async def resolve_multi_cart(
    cart_items: list[CartItem],
    deal_value: float,
) -> ClassificationResult:
    """Resolve insurance products for a multi-category cart.

    Applies the waterfall logic:
    1. Travel always wins primary slot
    2. Electronics > 5000 wins secondary slot
    3. Otherwise top 2 by confidence
    4. Never more than 2 products

    Args:
        cart_items: List of items in the cart
        deal_value: Total cart value in INR

    Returns:
        ClassificationResult with resolved products
    """
    if deal_value < 200:
        return ClassificationResult(
            top_products=[],
            cart_context="multi",
            show_offer=False,
            fallback_used=False,
            reason="deal_value_below_threshold",
        )

    if not cart_items:
        return ClassificationResult(
            top_products=[],
            cart_context="multi",
            show_offer=False,
            fallback_used=False,
            reason="empty_cart",
        )

    # Deduplicate by category - keep higher value item (edge case 6)
    category_items: dict[str, CartItem] = {}
    for item in cart_items:
        cat = item.category.lower()
        if cat not in category_items or item.deal_value > category_items[cat].deal_value:
            category_items[cat] = item

    # Collect all matches from each category
    all_matches: list[tuple[InsuranceMatch, str, float]] = []  # (match, category, deal_value)

    # Step 1: Check for travel
    travel_item = category_items.get("travel")
    travel_matches: list[InsuranceMatch] = []
    if travel_item:
        travel_matches = _apply_rules("travel", travel_item.subcategory, travel_item.deal_value)
        for m in travel_matches:
            all_matches.append((m, "travel", travel_item.deal_value))

    # Step 2: Check for qualifying electronics (> Rs 5000)
    electronics_item = category_items.get("electronics")
    electronics_matches: list[InsuranceMatch] = []
    if electronics_item and electronics_item.deal_value > 5000:
        electronics_matches = _apply_rules(
            "electronics", electronics_item.subcategory, electronics_item.deal_value
        )
        for m in electronics_matches:
            all_matches.append((m, "electronics", electronics_item.deal_value))

    # Step 3: If no travel, collect other category matches
    if not travel_matches:
        for cat, item in category_items.items():
            if cat in ("travel", "electronics"):
                continue
            matches = _apply_rules(cat, item.subcategory, item.deal_value)
            for m in matches:
                all_matches.append((m, cat, item.deal_value))

        # Also include electronics even if under threshold for confidence ranking
        if electronics_item and electronics_item.deal_value <= 5000:
            matches = _apply_rules(
                "electronics", electronics_item.subcategory, electronics_item.deal_value
            )
            for m in matches:
                all_matches.append((m, "electronics", electronics_item.deal_value))

    # Apply waterfall logic
    final_products: list[InsuranceMatch] = []
    used_product_ids: set[str] = set()

    # Waterfall Step 1: Travel takes primary slot
    if travel_matches:
        best_travel = max(travel_matches, key=lambda m: m.confidence)
        final_products.append(best_travel)
        used_product_ids.add(best_travel.product_id)

    # Waterfall Step 2: Qualifying electronics takes secondary
    if electronics_item and electronics_item.deal_value > 5000 and len(final_products) < 2:
        for m in electronics_matches:
            if m.product_id not in used_product_ids:
                final_products.append(m)
                used_product_ids.add(m.product_id)
                if len(final_products) >= 2:
                    break

    # Waterfall Step 3 & 4: Fill remaining slots by confidence
    if len(final_products) < 2:
        # Sort all remaining matches by confidence
        remaining = [
            m for m, cat, val in all_matches if m.product_id not in used_product_ids
        ]
        remaining.sort(key=lambda m: m.confidence, reverse=True)

        for m in remaining:
            if m.product_id not in used_product_ids:
                final_products.append(m)
                used_product_ids.add(m.product_id)
                if len(final_products) >= 2:
                    break

    # Step 5: Never more than 2
    final_products = final_products[:2]

    # Determine if we need to note more options
    unique_categories = len(category_items)
    note = None
    if unique_categories >= 3 and len(all_matches) > 2:
        note = f"{len(all_matches) - 2} more options available"

    return ClassificationResult(
        top_products=final_products,
        cart_context="multi",
        show_offer=True,
        fallback_used=False,
        reason=note,
    )


async def classify_deal_with_cart(deal: DealObject) -> ClassificationResult:
    """Classify a deal, handling both single and multi-cart scenarios.

    Args:
        deal: DealObject which may contain cart_items for multi-cart

    Returns:
        ClassificationResult
    """
    # Check if this is a multi-cart scenario
    if deal.cart_items and len(deal.cart_items) > 0:
        return await resolve_multi_cart(deal.cart_items, deal.deal_value)

    # Single item - use standard classification
    from insurance_engine.classifier import classify_intent

    return await classify_intent(
        merchant=deal.merchant,
        category=deal.category,
        subcategory=deal.subcategory,
        deal_value=deal.deal_value,
        user_history=deal.user_history.model_dump() if deal.user_history else None,
    )
