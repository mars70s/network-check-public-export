"""Tests for the individual check POST routes' event-loop-blocking fix (F2b).

Mirrors the approach used for the Multi Check API route (F2): these
tests verify that each POST handler now delegates its check call
through `run_in_threadpool` instead of calling it directly on the
event loop, and that the result still reaches the template context
unchanged. No real DNS/TLS/subprocess I/O is performed -- the check
functions and `templates` object are mocked at the module level.
"""

import unittest
from unittest.mock import AsyncMock, patch

import network_check.web.legacy as legacy


class _FakeRequest:
    """Handlers only forward this into template_context(); no
    attribute access happens before TemplateResponse is mocked out."""


class _RouteThreadpoolTestMixin:
    """Shared assertion helper: call a handler, confirm it delegated
    the check call through run_in_threadpool with the right function
    and argument, and that the returned result reached the template
    context unchanged."""

    async def _assert_delegates(
        self, handler, check_attr, input_kwarg, input_value, result_key, context_input_key
    ):
        fake_result = {"ok": True, "marker": check_attr}
        check_fn = getattr(legacy, check_attr)

        with patch.object(legacy, "run_in_threadpool", new=AsyncMock(return_value=fake_result)) as mocked_pool, \
             patch.object(legacy, "templates") as mocked_templates:
            mocked_templates.TemplateResponse.return_value = "RENDERED"
            response = await handler(_FakeRequest(), **{input_kwarg: input_value})

        mocked_pool.assert_awaited_once_with(check_fn, input_value)
        self.assertEqual(response, "RENDERED")

        _, context = mocked_templates.TemplateResponse.call_args.args
        self.assertIs(context[result_key], fake_result)
        self.assertEqual(context[context_input_key], input_value)


class RepresentativeRouteTests(_RouteThreadpoolTestMixin, unittest.IsolatedAsyncioTestCase):
    """One representative per blocking category, per the approved scope."""

    async def test_domain_dns_route(self) -> None:
        await self._assert_delegates(legacy.domain_post, "check_domain", "domain", "example.com", "result", "domain_input")

    async def test_tls_socket_route(self) -> None:
        await self._assert_delegates(legacy.tls_post, "check_tls", "domain", "example.com", "result", "domain_input")

    async def test_http2_subprocess_route(self) -> None:
        await self._assert_delegates(legacy.http2_post, "check_http2", "domain", "example.com", "result", "domain_input")

    async def test_security_headers_http_route(self) -> None:
        await self._assert_delegates(
            legacy.security_headers_post, "check_security_headers", "url", "https://example.com/", "result", "url_input"
        )


class RemainingRouteSmokeTests(_RouteThreadpoolTestMixin, unittest.IsolatedAsyncioTestCase):
    """Lightweight delegation-only smoke tests for the remaining routes."""

    async def test_dns_timing_route(self) -> None:
        await self._assert_delegates(legacy.dns_timing_post, "check_dns_timing", "domain", "example.com", "result", "domain_input")

    async def test_ip_preference_route(self) -> None:
        await self._assert_delegates(legacy.ip_preference_post, "check_ip_preference", "domain", "example.com", "result", "domain_input")

    async def test_mx_route(self) -> None:
        await self._assert_delegates(legacy.mx_post, "check_mx_records", "domain", "example.com", "result", "domain_input")

    async def test_spf_route(self) -> None:
        await self._assert_delegates(legacy.spf_post, "check_spf_records", "domain", "example.com", "result", "domain_input")

    async def test_dmarc_route(self) -> None:
        await self._assert_delegates(legacy.dmarc_post, "check_dmarc_records", "domain", "example.com", "result", "domain_input")

    async def test_caa_route(self) -> None:
        await self._assert_delegates(legacy.caa_post, "check_caa", "domain", "example.com", "result", "domain_input")

    async def test_ptr_route(self) -> None:
        await self._assert_delegates(legacy.ptr_post, "check_ptr", "ip_input", "192.0.2.1", "result", "ip_input")


if __name__ == "__main__":
    unittest.main()
