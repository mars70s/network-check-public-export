"""Deterministic, no-network checks for outbound destination preflight."""

import socket
import sys
import types
import unittest
from unittest.mock import patch


def _install_dns_import_stub_if_needed() -> None:
    """Allow preflight-only tests to run when the runtime DNS dependency is absent."""
    try:
        import dns.exception  # noqa: F401
        import dns.resolver  # noqa: F401
    except ModuleNotFoundError as exc:
        if exc.name != "dns":
            raise

        exception = types.ModuleType("dns.exception")
        exception.Timeout = type("Timeout", (Exception,), {})
        resolver = types.ModuleType("dns.resolver")
        resolver.Resolver = object
        resolver.NoAnswer = type("NoAnswer", (Exception,), {})
        resolver.NXDOMAIN = type("NXDOMAIN", (Exception,), {})
        resolver.NoNameservers = type("NoNameservers", (Exception,), {})
        dns = types.ModuleType("dns")
        dns.exception = exception
        dns.resolver = resolver
        sys.modules.update({"dns": dns, "dns.exception": exception, "dns.resolver": resolver})


_install_dns_import_stub_if_needed()

from network_check.checks.destination_guard import (  # noqa: E402
    is_disallowed_target_ip,
    resolve_public_host_for_connect,
)
from network_check.checks.http2 import check_http2  # noqa: E402
from network_check.checks.tls import check_tls  # noqa: E402


class DestinationGuardTests(unittest.TestCase):
    def test_prohibited_ipv4_addresses_are_rejected(self) -> None:
        for address in ("127.0.0.1", "10.0.0.1", "169.254.1.1", "192.0.2.1"):
            with self.subTest(address=address):
                self.assertTrue(is_disallowed_target_ip(address))

    def test_prohibited_ipv6_addresses_are_rejected(self) -> None:
        for address in ("::1", "fc00::1", "fe80::1", "ff00::1"):
            with self.subTest(address=address):
                self.assertTrue(is_disallowed_target_ip(address))

    def test_mixed_dns_answers_reject_the_destination(self) -> None:
        answers = [
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("8.8.8.8", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("10.0.0.1", 443)),
        ]
        with patch(
            "network_check.checks.destination_guard.socket.getaddrinfo",
            return_value=answers,
        ):
            result = resolve_public_host_for_connect("example.com", 443)

        self.assertFalse(result["ok"])
        self.assertEqual(result["blocked_ips"], ["10.0.0.1"])

    def test_tls_rejects_before_opening_a_connection(self) -> None:
        with (
            patch(
                "network_check.checks.tls.assert_public_connect_target",
                return_value={"ok": False, "error": "blocked"},
            ),
            patch("network_check.checks.tls.open_validated_tcp_socket") as open_socket,
        ):
            result = check_tls("example.com")

        self.assertEqual(result["guard"], "destination_safety")
        open_socket.assert_not_called()

    def test_http2_rejects_before_running_curl(self) -> None:
        with (
            patch(
                "network_check.checks.http2.assert_public_connect_target",
                return_value={"ok": False, "error": "blocked"},
            ),
            patch("network_check.checks.http2.subprocess.run") as run,
        ):
            result = check_http2("example.com")

        self.assertEqual(result["guard"], "destination_safety")
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
