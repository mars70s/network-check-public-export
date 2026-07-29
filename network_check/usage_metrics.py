from __future__ import annotations

import os
import sqlite3

from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

DEFAULT_USAGE_DB = "usage_metrics.sqlite3"
USAGE_DB_ENV = "NETWORK_CHECK_USAGE_DB"
SQLITE_CONNECT_TIMEOUT = 0.25


SCHEMA = """
CREATE TABLE IF NOT EXISTS public_usage_daily (
    event_date TEXT NOT NULL,
    event_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (event_date, event_type, target_id)
)
"""


def usage_db_path() -> Path:
    configured_path = os.getenv(USAGE_DB_ENV, DEFAULT_USAGE_DB)
    return Path(configured_path)


def _ensure_parent_directory(db_path: Path) -> None:
    parent = db_path.parent
    if parent != Path("."):
        parent.mkdir(parents=True, exist_ok=True)


def _connect() -> sqlite3.Connection:
    db_path = usage_db_path()
    _ensure_parent_directory(db_path)
    connection = sqlite3.connect(db_path, timeout=SQLITE_CONNECT_TIMEOUT)
    connection.row_factory = sqlite3.Row
    return connection


def _iso_days_ago(days: int) -> str:
    return (date.today() - timedelta(days=days)).isoformat()


def _rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def init_usage_db() -> None:
    with closing(_connect()) as connection:
        connection.execute(SCHEMA)
        connection.commit()


def record_usage_event(event_type: str, target_id: str, count: int = 1) -> bool:
    """Record a daily aggregate usage event.

    This function intentionally accepts only internal event names and target IDs.
    It must not be called with user-entered domain names, IP addresses, URLs,
    headers, cookies, sessions, request bodies, or check results.

    Metrics failure must not break normal Network Check behavior, so errors are
    swallowed and reported as False to the caller.
    """

    if count <= 0:
        return False
    if not event_type or not target_id:
        return False

    event_date = date.today().isoformat()
    updated_at = datetime.now().isoformat(timespec="seconds")

    try:
        with closing(_connect()) as connection:
            connection.execute(SCHEMA)
            connection.execute(
                """
                INSERT INTO public_usage_daily (
                    event_date,
                    event_type,
                    target_id,
                    count,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(event_date, event_type, target_id)
                DO UPDATE SET
                    count = count + excluded.count,
                    updated_at = excluded.updated_at
                """,
                (event_date, event_type, target_id, count, updated_at),
            )
            connection.commit()
        return True
    except Exception:
        return False


def get_usage_summary(limit: int = 200) -> list[dict[str, Any]]:
    safe_limit = max(1, min(limit, 1000))
    with closing(_connect()) as connection:
        connection.execute(SCHEMA)
        rows = connection.execute(
            """
            SELECT
                event_date,
                event_type,
                target_id,
                count,
                updated_at
            FROM public_usage_daily
            ORDER BY event_date DESC, event_type ASC, count DESC, target_id ASC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()
    return _rows_to_dicts(rows)


def get_usage_dashboard() -> dict[str, Any]:
    """Return dashboard aggregates from existing anonymous daily counters.

    This function does not add new tracking fields and does not read or expose
    user-entered domains, IP addresses, headers, cookies, sessions, request
    bodies, or check results.
    """

    today = date.today().isoformat()
    last_7_start = _iso_days_ago(6)
    last_30_start = _iso_days_ago(29)

    with closing(_connect()) as connection:
        connection.execute(SCHEMA)

        def total_since(start_date: str | None = None) -> int:
            if start_date is None:
                row = connection.execute(
                    "SELECT COALESCE(SUM(count), 0) AS total FROM public_usage_daily"
                ).fetchone()
            else:
                row = connection.execute(
                    """
                    SELECT COALESCE(SUM(count), 0) AS total
                    FROM public_usage_daily
                    WHERE event_date >= ?
                    """,
                    (start_date,),
                ).fetchone()
            return int(row["total"])

        def popular_checks(start_date: str | None = None) -> list[dict[str, Any]]:
            if start_date is None:
                rows = connection.execute(
                    """
                    SELECT
                        target_id,
                        SUM(count) AS count,
                        MAX(updated_at) AS updated_at
                    FROM public_usage_daily
                    WHERE event_type = 'multi_check_selected'
                    GROUP BY target_id
                    ORDER BY count DESC, target_id ASC
                    LIMIT 20
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT
                        target_id,
                        SUM(count) AS count,
                        MAX(updated_at) AS updated_at
                    FROM public_usage_daily
                    WHERE event_type = 'multi_check_selected'
                      AND event_date >= ?
                    GROUP BY target_id
                    ORDER BY count DESC, target_id ASC
                    LIMIT 20
                    """,
                    (start_date,),
                ).fetchall()
            return _rows_to_dicts(rows)

        summary_totals = [
            {
                "label": "今日",
                "period": today,
                "count": total_since(today),
            },
            {
                "label": "過去7日",
                "period": f"{last_7_start} 以降",
                "count": total_since(last_7_start),
            },
            {
                "label": "過去30日",
                "period": f"{last_30_start} 以降",
                "count": total_since(last_30_start),
            },
            {
                "label": "全期間",
                "period": "all time",
                "count": total_since(),
            },
        ]

        event_target_totals = connection.execute(
            """
            SELECT
                event_type,
                target_id,
                SUM(count) AS count,
                MAX(updated_at) AS updated_at
            FROM public_usage_daily
            WHERE event_date >= ?
            GROUP BY event_type, target_id
            ORDER BY count DESC, event_type ASC, target_id ASC
            LIMIT 200
            """,
            (last_30_start,),
        ).fetchall()

        daily_rows = connection.execute(
            """
            SELECT
                event_date,
                event_type,
                target_id,
                count,
                updated_at
            FROM public_usage_daily
            WHERE event_date >= ?
            ORDER BY event_date DESC, event_type ASC, count DESC, target_id ASC
            LIMIT 1000
            """,
            (last_30_start,),
        ).fetchall()

        popular_check_groups = {
            "last_7_days": popular_checks(last_7_start),
            "last_30_days": popular_checks(last_30_start),
            "all_time": popular_checks(),
        }

        return {
            "summary_totals": summary_totals,
            "event_target_totals": _rows_to_dicts(event_target_totals),
            "popular_checks": popular_check_groups,
            "daily_rows": _rows_to_dicts(daily_rows),
        }


def usage_metrics_status() -> dict[str, str]:
    db_path = usage_db_path()
    return {
        "db_path": str(db_path),
        "db_exists": "yes" if db_path.exists() else "no",
    }
