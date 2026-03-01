"""Insurance Catalog Management.

Load and query the insurance product catalog.
"""

import json
import os
from functools import lru_cache
from pathlib import Path

from mcp_server.schemas import InsuranceProduct


def _get_catalog_path() -> Path:
    """Get the path to the catalog file."""
    catalog_path = os.environ.get("CATALOG_PATH", "./data/insurance_catalog.json")
    path = Path(catalog_path)
    if not path.exists():
        # Try relative to module location
        path = Path(__file__).parent.parent / "data" / "insurance_catalog.json"
    return path


@lru_cache(maxsize=1)
def load_catalog() -> tuple[InsuranceProduct, ...]:
    """Load the insurance catalog from JSON file.

    Returns:
        Tuple of InsuranceProduct objects (cached)
    """
    path = _get_catalog_path()
    with open(path) as f:
        data = json.load(f)
    return tuple(InsuranceProduct(**item) for item in data)


def reload_catalog() -> tuple[InsuranceProduct, ...]:
    """Force reload the catalog (clears cache).

    Returns:
        Tuple of InsuranceProduct objects
    """
    load_catalog.cache_clear()
    return load_catalog()


def lookup_by_id(product_id: str) -> InsuranceProduct | None:
    """Find a product by its ID.

    Args:
        product_id: The product ID to look up (e.g., "TRVL_CANCEL")

    Returns:
        InsuranceProduct if found, None otherwise
    """
    catalog = load_catalog()
    for product in catalog:
        if product.id == product_id:
            return product
    return None


def lookup_by_category_triggers(
    category: str,
    subcategory: str | None = None,
) -> list[InsuranceProduct]:
    """Find products matching category and optionally subcategory triggers.

    Args:
        category: The category to match (e.g., "travel", "electronics")
        subcategory: Optional subcategory to match

    Returns:
        List of matching InsuranceProduct objects
    """
    catalog = load_catalog()
    matches = []
    category_lower = category.lower()
    subcategory_lower = subcategory.lower() if subcategory else None

    for product in catalog:
        # Check category triggers
        if category_lower not in [t.lower() for t in product.category_triggers]:
            continue

        # If subcategory specified, check subcategory triggers
        if subcategory_lower:
            subcategory_triggers_lower = [t.lower() for t in product.subcategory_triggers]
            # Wildcard matches all subcategories
            if "*" in product.subcategory_triggers:
                matches.append(product)
            elif subcategory_lower in subcategory_triggers_lower:
                matches.append(product)
        else:
            # No subcategory filter, include all category matches
            matches.append(product)

    return matches


def get_all_products() -> list[InsuranceProduct]:
    """Get all products in the catalog.

    Returns:
        List of all InsuranceProduct objects
    """
    return list(load_catalog())


def get_product_ids() -> list[str]:
    """Get all product IDs.

    Returns:
        List of product ID strings
    """
    return [p.id for p in load_catalog()]
