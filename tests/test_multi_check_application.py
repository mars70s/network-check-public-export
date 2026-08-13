"""Application-layer tests for Domain Multi Check (network_check.application.multi_check).

These are distinct from tests/test_multi_check_api.py, which only
covers the route/threadpool-delegation layer. Here we exercise
run_multi_check() directly with a valid payload -- something the API
route tests deliberately avoided to steer clear of real network I/O.

All check execution here uses fake functions swapped in via
unittest.mock.patch.dict on the real MULTI_CHECK_FUNCTIONS registry
dict (the same object network_check.application.multi_check imported
a reference to). No real DNS/TLS/HTTP/curl/network access occurs.
"""

import unittest
from unittest.mock import Mock, patch

from network_check.application.multi_check import run_multi_check
from network_check.checks.registry import MULTI_CHECK_EXECUTION_ORDER


class MultiCheckSelectionAndOrderTests(unittest.TestCase):
    def test_only_selected_checks_execute(self) -> None:
        selected_fn = Mock(return_value={"ok": True, "id": "mx"})
        not_selected_fn = Mock(return_value={"ok": True, "id": "spf"})

        with patch.dict(
            "network_check.checks.registry.MULTI_CHECK_FUNCTIONS",
            {"mx": selected_fn, "spf": not_selected_fn},
        ):
            result = run_multi_check(
                {"domain": "example.com", "checks": ["mx"]}, record_usage=None
            )

        self.assertTrue(result["ok"])
        self.assertEqual(list(result["results"].keys()), ["mx"])
        selected_fn.assert_called_once_with("example.com")
        not_selected_fn.assert_not_called()

    def test_execution_order_matches_registry_order_not_payload_order(self) -> None:
        fakes = {
            check_id: Mock(return_value={"ok": True, "id": check_id})
            for check_id in ("domain", "mx", "caa")
        }

        with patch.dict("network_check.checks.registry.MULTI_CHECK_FUNCTIONS", fakes):
            # Payload lists them in a scrambled order deliberately different
            # from MULTI_CHECK_EXECUTION_ORDER.
            result = run_multi_check(
                {"domain": "example.com", "checks": ["caa", "domain", "mx"]},
                record_usage=None,
            )

        expected_order = [
            check_id
            for check_id in MULTI_CHECK_EXECUTION_ORDER
            if check_id in {"domain", "mx", "caa"}
        ]
        self.assertEqual(list(result["results"].keys()), expected_order)
        self.assertNotEqual(list(result["results"].keys()), ["caa", "domain", "mx"])


class MultiCheckFailureIsolationTests(unittest.TestCase):
    def test_failure_in_one_check_does_not_prevent_others(self) -> None:
        def _raising_check(domain: str) -> dict:
            raise RuntimeError("simulated failure")

        ok_fn = Mock(return_value={"ok": True, "id": "spf"})

        with patch.dict(
            "network_check.checks.registry.MULTI_CHECK_FUNCTIONS",
            {"mx": _raising_check, "spf": ok_fn},
        ):
            result = run_multi_check(
                {"domain": "example.com", "checks": ["mx", "spf"]}, record_usage=None
            )

        self.assertTrue(result["ok"])
        self.assertFalse(result["results"]["mx"]["ok"])
        self.assertIn("mx", result["errors"])
        self.assertTrue(result["results"]["spf"]["ok"])
        self.assertNotIn("spf", result["errors"])
        ok_fn.assert_called_once_with("example.com")


class MultiCheckInvalidSelectionTests(unittest.TestCase):
    def test_unsupported_check_id_is_rejected(self) -> None:
        result = run_multi_check(
            {"domain": "example.com", "checks": ["not-a-real-check"]}, record_usage=None
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["results"], {})
        self.assertIn("checks", result["errors"])


if __name__ == "__main__":
    unittest.main()
