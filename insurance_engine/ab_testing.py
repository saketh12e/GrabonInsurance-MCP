"""A/B Testing Framework.

Uses aiosqlite for async-safe database operations.
Deterministic variant assignment using hash(session_id + product_id) % 3.
"""

import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Literal

import aiosqlite

from mcp_server.schemas import ABSession, DashboardData, VariantStats

# Variant mapping
VARIANTS: list[Literal["urgency", "value", "social_proof"]] = [
    "urgency",
    "value",
    "social_proof",
]


def _get_db_path() -> Path:
    """Get the database file path."""
    db_path = os.environ.get("AB_DB_PATH", "./data/ab_events.db")
    return Path(db_path)


async def _init_db(db: aiosqlite.Connection) -> None:
    """Initialize the database schema if not exists."""
    await db.execute("""
        CREATE TABLE IF NOT EXISTS ab_sessions (
            session_id TEXT PRIMARY KEY,
            deal_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            variant TEXT NOT NULL,
            product_id TEXT NOT NULL,
            copy_string TEXT NOT NULL,
            shown_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            converted INTEGER DEFAULT 0,
            converted_at TIMESTAMP,
            event_type TEXT DEFAULT 'impression'
        )
    """)
    await db.commit()


async def _get_db() -> aiosqlite.Connection:
    """Get database connection with auto-init."""
    db_path = _get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = await aiosqlite.connect(str(db_path))
    await _init_db(db)
    return db


def get_variant(session_id: str, product_id: str) -> Literal["urgency", "value", "social_proof"]:
    """Deterministically assign variant based on session and product.

    Uses hash(session_id + product_id) % 3 for stable assignment.

    Args:
        session_id: Unique session identifier
        product_id: Insurance product ID

    Returns:
        One of: "urgency", "value", "social_proof"
    """
    combined = f"{session_id}{product_id}"
    hash_value = int(hashlib.sha256(combined.encode()).hexdigest(), 16)
    variant_index = hash_value % 3
    return VARIANTS[variant_index]


async def record_impression(
    session_id: str,
    deal_id: str,
    user_id: str,
    product_id: str,
    copy_string: str,
) -> ABSession:
    """Record an A/B test impression.

    Args:
        session_id: Unique session identifier
        deal_id: Deal being shown
        user_id: User seeing the offer
        product_id: Insurance product shown
        copy_string: Generated copy string

    Returns:
        ABSession object with assigned variant
    """
    variant = get_variant(session_id, product_id)
    shown_at = datetime.now()

    db = await _get_db()
    try:
        # Check if session already exists
        cursor = await db.execute(
            "SELECT session_id, variant FROM ab_sessions WHERE session_id = ?",
            (session_id,),
        )
        existing = await cursor.fetchone()

        event_type = "impression"
        if existing:
            # Session already has a variant assigned
            # Check if all 3 variants have been seen (edge case 10)
            cursor = await db.execute(
                """
                SELECT COUNT(DISTINCT variant) FROM ab_sessions
                WHERE user_id = ? AND product_id = ?
                """,
                (user_id, product_id),
            )
            count = (await cursor.fetchone())[0]
            if count >= 3:
                event_type = "repeat_exposure"

            # Update existing session with new impression
            await db.execute(
                """
                UPDATE ab_sessions
                SET copy_string = ?, shown_at = ?, event_type = ?
                WHERE session_id = ?
                """,
                (copy_string, shown_at.isoformat(), event_type, session_id),
            )
        else:
            # Insert new session
            await db.execute(
                """
                INSERT INTO ab_sessions
                (session_id, deal_id, user_id, variant, product_id, copy_string, shown_at, event_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    deal_id,
                    user_id,
                    variant,
                    product_id,
                    copy_string,
                    shown_at.isoformat(),
                    event_type,
                ),
            )
        await db.commit()
    finally:
        await db.close()

    return ABSession(
        session_id=session_id,
        deal_id=deal_id,
        user_id=user_id,
        variant=variant,
        product_id=product_id,
        copy_string=copy_string,
        shown_at=shown_at,
        converted=False,
        converted_at=None,
    )


async def record_conversion(session_id: str, product_id: str) -> datetime | None:
    """Record a conversion event.

    Args:
        session_id: A/B session ID
        product_id: Product that was converted

    Returns:
        Conversion timestamp if successful, None otherwise
    """
    db = await _get_db()
    try:
        converted_at = datetime.now()
        cursor = await db.execute(
            """
            UPDATE ab_sessions
            SET converted = 1, converted_at = ?
            WHERE session_id = ? AND product_id = ?
            """,
            (converted_at.isoformat(), session_id, product_id),
        )
        await db.commit()

        if cursor.rowcount > 0:
            return converted_at
        return None
    finally:
        await db.close()


async def get_dashboard_data() -> DashboardData:
    """Get A/B testing dashboard metrics.

    Returns:
        DashboardData with variant stats, totals, and overall CVR
    """
    db = await _get_db()
    try:
        # Get stats per variant
        cursor = await db.execute("""
            SELECT
                variant,
                COUNT(*) as impressions,
                SUM(converted) as conversions
            FROM ab_sessions
            GROUP BY variant
        """)
        rows = await cursor.fetchall()

        variant_stats = []
        total_impressions = 0
        total_conversions = 0
        best_cvr = -1.0
        best_variant = None

        for row in rows:
            variant, impressions, conversions = row
            conversions = conversions or 0
            cvr = (conversions / impressions * 100) if impressions > 0 else 0.0

            total_impressions += impressions
            total_conversions += conversions

            if cvr > best_cvr:
                best_cvr = cvr
                best_variant = variant

            variant_stats.append(
                VariantStats(
                    variant=variant,
                    impressions=impressions,
                    conversions=conversions,
                    cvr_percent=round(cvr, 2),
                    is_best=False,
                )
            )

        # Mark best performer
        for stat in variant_stats:
            if stat.variant == best_variant:
                stat.is_best = True

        # Ensure all variants are represented
        existing_variants = {s.variant for s in variant_stats}
        for v in VARIANTS:
            if v not in existing_variants:
                variant_stats.append(
                    VariantStats(
                        variant=v,
                        impressions=0,
                        conversions=0,
                        cvr_percent=0.0,
                        is_best=False,
                    )
                )

        overall_cvr = (
            (total_conversions / total_impressions * 100)
            if total_impressions > 0
            else 0.0
        )

        return DashboardData(
            variants=variant_stats,
            total_impressions=total_impressions,
            total_conversions=total_conversions,
            overall_cvr_percent=round(overall_cvr, 2),
        )
    finally:
        await db.close()


async def clear_test_data() -> None:
    """Clear all A/B test data (for testing purposes)."""
    db = await _get_db()
    try:
        await db.execute("DELETE FROM ab_sessions")
        await db.commit()
    finally:
        await db.close()
