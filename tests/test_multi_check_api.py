"""Tests for the Multi Check API route's event-loop-blocking fix.

These tests do not perform real network I/O. They verify that
`multi_check_run` (1) delegates execution to a thread via
`run_in_threadpool` instead of calling `run_multi_check` directly on
the event loop, (2) preserves the exact result/error contract of
`run_multi_check`, and (3) that delegating a blocking call through
`run_in_threadpool` actually keeps the event loop free, using the
same primitive the route now uses.
"""

import asyncio
import time
import unittest
from unittest.mock import AsyncMock, patch

from starlette.concurrency import run_in_threadpool

import network_check.web.api as api


class _FakeRequest:
    """Minimal stand-in for a Starlette Request; only `.json()` is used."""

    def __init__(self, payload):
        self._payload = payload

    async def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class MultiCheckApiThreadpoolTests(unittest.IsolatedAsyncioTestCase):
    async def test_multi_check_run_delegates_to_threadpool(self) -> None:
        payload = {"domain": "example.com", "checks": ["domain"]}

        with patch.object(api, "run_in_threadpool", new=AsyncMock(return_value={"ok": True})) as mocked:
            result = await api.multi_check_run(_FakeRequest(payload))

        mocked.assert_awaited_once_with(
            api.run_multi_check,
            payload,
            record_usage=api.record_usage_event,
        )
        self.assertEqual(result, {"ok": True})

    async def test_invalid_payload_matches_direct_run_multi_check_call(self) -> None:
        # payload=None triggers run_multi_check's existing _invalid_request()
        # path, which does no I/O, so this exercises the real call end to end
        # through the new threadpool wrapper without touching the network.
        direct_result = api.run_multi_check(None, record_usage=None)
        routed_result = await api.multi_check_run(_FakeRequest(None))

        self.assertEqual(routed_result, direct_result)
        self.assertFalse(routed_result["ok"])
        self.assertEqual(routed_result["errors"], {})

    async def test_json_parse_failure_still_falls_back_to_invalid_request(self) -> None:
        routed_result = await api.multi_check_run(_FakeRequest(ValueError("bad json")))

        self.assertFalse(routed_result["ok"])
        self.assertEqual(routed_result["results"], {})


class ThreadpoolKeepsEventLoopFreeTests(unittest.IsolatedAsyncioTestCase):
    async def test_blocking_call_via_run_in_threadpool_does_not_block_event_loop(self) -> None:
        """Deterministic proof that the mechanism the route now uses
        (run_in_threadpool) frees the event loop for other coroutines,
        the same property F2 required for the Multi Check route."""

        events: list[str] = []

        def blocking_sleep() -> str:
            time.sleep(0.3)
            return "slow-done"

        async def fast_coroutine() -> None:
            await asyncio.sleep(0.05)
            events.append("fast-done")

        slow_task = asyncio.create_task(run_in_threadpool(blocking_sleep))
        fast_task = asyncio.create_task(fast_coroutine())

        await fast_task
        # The fast coroutine must complete well before the slow blocking
        # call, proving the event loop was not held by the blocking work.
        self.assertEqual(events, ["fast-done"])
        self.assertFalse(slow_task.done())

        slow_result = await slow_task
        self.assertEqual(slow_result, "slow-done")


if __name__ == "__main__":
    unittest.main()
