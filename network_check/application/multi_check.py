from __future__ import annotations

from collections.abc import Callable
from typing import Any

from network_check.checks.registry import (
    MULTI_CHECK_EXECUTION_ORDER,
    MULTI_CHECK_FUNCTIONS,
)

UsageEventRecorder = Callable[[str, str], object]

CHECK_FAILURE_ERROR = "Check failed."


def _record_usage_safely(
    recorder: UsageEventRecorder | None,
    event_type: str,
    target_id: str,
) -> None:
    if recorder is None:
        return

    try:
        recorder(event_type, target_id)
    except Exception:
        return


def _invalid_request() -> dict[str, Any]:
    return {
        "ok": False,
        "error": "Invalid request.",
        "results": {},
        "errors": {},
    }


def run_multi_check(
    payload: object,
    *,
    record_usage: UsageEventRecorder | None = None,
) -> dict[str, Any]:
    """Execute the stable domain-based Multi Check request contract.

    This application service owns request validation, selected-check validation,
    deterministic dispatch, result wrapping, and per-check failure isolation.
    It deliberately has no FastAPI, template, static-asset, or UI-catalog
    dependency.
    """

    domain = payload.get("domain") if isinstance(payload, dict) else None
    checks = payload.get("checks") if isinstance(payload, dict) else None

    if not isinstance(domain, str) or not domain.strip() or not isinstance(checks, list):
        return _invalid_request()

    selected_checks: list[str] = []
    invalid_checks: list[object] = []

    for check_id in checks:
        if not isinstance(check_id, str) or check_id not in MULTI_CHECK_FUNCTIONS:
            invalid_checks.append(check_id)
            continue
        if check_id not in selected_checks:
            selected_checks.append(check_id)

    if invalid_checks or not selected_checks:
        return {
            "ok": False,
            "domain": domain.strip(),
            "error": "Invalid request.",
            "results": {},
            "errors": {
                "checks": "Unknown or unsupported check id.",
            },
        }

    _record_usage_safely(record_usage, "multi_check_run", "all")
    for check_id in selected_checks:
        _record_usage_safely(record_usage, "multi_check_selected", check_id)

    results: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}

    for check_id in MULTI_CHECK_EXECUTION_ORDER:
        if check_id not in selected_checks:
            continue

        check_function = MULTI_CHECK_FUNCTIONS[check_id]
        try:
            result = check_function(domain)
            results[check_id] = {
                "ok": bool(result.get("ok")),
                "result": result,
            }
        except Exception:
            error_result = {
                "ok": False,
                "domain": domain.strip(),
                "error": CHECK_FAILURE_ERROR,
            }
            results[check_id] = {
                "ok": False,
                "result": error_result,
            }
            errors[check_id] = CHECK_FAILURE_ERROR

    return {
        "ok": True,
        "domain": domain.strip(),
        "results": results,
        "errors": errors,
    }
