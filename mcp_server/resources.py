"""MCP Resources for GrabInsurance.

Provides the insurance://catalog resource that returns the full catalog
as a formatted string for Claude to load before classification.
"""

import json
import os
from pathlib import Path


def get_insurance_catalog() -> str:
    """Return the full insurance catalog as a formatted string.

    This resource provides Claude with complete product context before
    performing any classification. The catalog includes all 8 insurance
    products with their triggers, rates, and descriptions.

    Returns:
        Formatted string representation of the insurance catalog
    """
    catalog_path = os.environ.get("CATALOG_PATH", "./data/insurance_catalog.json")
    path = Path(catalog_path)
    if not path.exists():
        # Try relative to script location
        path = Path(__file__).parent.parent / "data" / "insurance_catalog.json"

    try:
        with open(path) as f:
            catalog = json.load(f)
    except FileNotFoundError:
        return "ERROR: Insurance catalog not found"
    except json.JSONDecodeError:
        return "ERROR: Invalid catalog JSON"

    # Format as readable string
    lines = ["# GrabInsurance Product Catalog", ""]
    lines.append(f"Total Products: {len(catalog)}")
    lines.append("")

    for product in catalog:
        lines.append(f"## {product['name']} ({product['id']})")
        lines.append(f"- Category Triggers: {', '.join(product['category_triggers'])}")
        lines.append(f"- Subcategory Triggers: {', '.join(product['subcategory_triggers'])}")
        lines.append(f"- Base Premium Rate: {product['base_premium_rate']}")
        lines.append(f"- Coverage Multiplier: {product['coverage_multiplier']}x")
        lines.append(f"- Description: {product['description']}")
        lines.append("")

    return "\n".join(lines)


def get_catalog_json() -> list[dict]:
    """Return the raw catalog as a list of dicts.

    Returns:
        List of insurance product dictionaries
    """
    catalog_path = os.environ.get("CATALOG_PATH", "./data/insurance_catalog.json")
    path = Path(catalog_path)
    if not path.exists():
        path = Path(__file__).parent.parent / "data" / "insurance_catalog.json"

    with open(path) as f:
        return json.load(f)
