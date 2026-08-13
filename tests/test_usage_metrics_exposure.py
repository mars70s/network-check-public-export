"""Tests for the usage-metrics-related additional finding:

A. network_check/web/metrics.py must not surface raw exception text
   from get_usage_dashboard() to the user.
B. templates/usage_metrics.html (and the context that reaches it)
   must not disclose the filesystem path of the usage metrics DB.
C. Normal usage-metrics display (db_exists, usage_dashboard) must
   still work.

All checks are done against the template context actually handed to
TemplateResponse (mocked out, following the same approach used for
the individual check routes), which proves the leak-prone value never
reaches the template layer -- not just that the current template
happens not to render it. No real DB/network access occurs.
"""

import unittest
from unittest.mock import AsyncMock, patch

import network_check.web.metrics as metrics

MARKER = "MARKER-should-never-reach-the-template"
FAKE_ABSOLUTE_DB_PATH = "/opt/repos/network-check/private/usage_metrics.sqlite3"


class _FakeRequest:
    pass


async def _call_route_and_capture_context():
    with patch.object(metrics, "templates") as mocked_templates:
        mocked_templates.TemplateResponse.return_value = "RENDERED"
        response = await metrics.usage_metrics(_FakeRequest())
    _, context = mocked_templates.TemplateResponse.call_args.args
    return response, context


class RawExceptionSanitizationTests(unittest.IsolatedAsyncioTestCase):
    async def test_dashboard_exception_omits_raw_detail(self) -> None:
        with patch.object(
            metrics, "get_usage_dashboard", side_effect=RuntimeError(MARKER)
        ):
            response, context = await _call_route_and_capture_context()

        self.assertEqual(response, "RENDERED")
        self.assertNotIn(MARKER, repr(context))
        self.assertEqual(
            context["metrics_error"],
            "Usage metrics are temporarily unavailable. / 利用状況の集計を一時的に表示できません。",
        )
        self.assertEqual(context["usage_dashboard"], {})

    async def test_normal_dashboard_result_has_no_error(self) -> None:
        fake_dashboard = {"summary_totals": [], "popular_checks": {}, "daily_rows": []}
        with patch.object(metrics, "get_usage_dashboard", return_value=fake_dashboard):
            response, context = await _call_route_and_capture_context()

        self.assertEqual(response, "RENDERED")
        self.assertIsNone(context["metrics_error"])
        self.assertEqual(context["usage_dashboard"], fake_dashboard)


class DbPathNonDisclosureTests(unittest.IsolatedAsyncioTestCase):
    async def test_db_path_never_reaches_template_context(self) -> None:
        with patch.object(
            metrics,
            "usage_metrics_status",
            return_value={"db_path": FAKE_ABSOLUTE_DB_PATH, "db_exists": "yes"},
        ):
            _, context = await _call_route_and_capture_context()

        self.assertNotIn(FAKE_ABSOLUTE_DB_PATH, repr(context))
        self.assertNotIn("db_path", context["metrics_status"])

    async def test_db_exists_is_preserved(self) -> None:
        with patch.object(
            metrics,
            "usage_metrics_status",
            return_value={"db_path": FAKE_ABSOLUTE_DB_PATH, "db_exists": "yes"},
        ):
            _, context = await _call_route_and_capture_context()

        self.assertEqual(context["metrics_status"], {"db_exists": "yes"})


if __name__ == "__main__":
    unittest.main()
