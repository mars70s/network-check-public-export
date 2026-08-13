"""Tests for F5: user-facing check errors must not leak raw exception
text, library/OS internals, subprocess command detail, or resolver
error strings. All network I/O is mocked; nothing here touches a real
socket, DNS resolver, or subprocess.

Each test plants a distinctive, unmistakable marker string inside the
mocked exception and asserts that marker never appears in the
check's user-facing "error" (or nested "detail"/"error") output.
"""

import socket
import subprocess
import unittest
from unittest.mock import MagicMock, Mock, patch

import dns.exception
import dns.resolver

from network_check.checks.caa import check_caa
from network_check.checks.destination_guard import resolve_public_host_for_connect
from network_check.checks.dns_timing import check_dns_timing
from network_check.checks.http2 import check_http2
from network_check.checks.mail import check_dmarc_records, check_mx_records, check_spf_records
from network_check.checks.ptr import check_ptr
from network_check.checks.security_headers import (
    check_security_headers,
    normalize_security_header_url,
)
from network_check.checks.tls import check_tls

MARKER = "MARKER-internal-detail-should-never-be-user-visible"


def _all_text(value) -> str:
    """Flatten a result dict to a single string for substring checks."""
    return repr(value)


class TlsSanitizationTests(unittest.TestCase):
    def test_unexpected_exception_omits_raw_detail(self) -> None:
        with (
            patch(
                "network_check.checks.tls.assert_public_connect_target",
                return_value={"ok": True, "candidates": [object()]},
            ),
            patch(
                "network_check.checks.tls.open_validated_tcp_socket",
                side_effect=RuntimeError(MARKER),
            ),
        ):
            result = check_tls("example.com")

        self.assertNotIn(MARKER, _all_text(result))
        self.assertEqual(result["error"], "TLS connection failed. / TLS接続に失敗しました。")


class Http2SanitizationTests(unittest.TestCase):
    def test_subprocess_exception_omits_raw_detail(self) -> None:
        with (
            patch(
                "network_check.checks.http2.assert_public_connect_target",
                return_value={"ok": True, "candidates": [object()]},
            ),
            patch(
                "network_check.checks.http2.subprocess.run",
                side_effect=subprocess.TimeoutExpired(
                    cmd=["curl", "--resolve", f"example.com:443:{MARKER}"], timeout=5
                ),
            ),
        ):
            result = check_http2("example.com")

        self.assertNotIn(MARKER, _all_text(result))
        self.assertEqual(result["error"], "HTTP/2 check failed. / HTTP/2確認に失敗しました。")


class MailSanitizationTests(unittest.TestCase):
    def _mock_resolver(self, side_effect):
        resolver = MagicMock()
        resolver.resolve.side_effect = side_effect
        return patch("network_check.checks.mail.create_dns_resolver", return_value=resolver)

    def test_mx_unexpected_exception_omits_raw_detail(self) -> None:
        with self._mock_resolver(RuntimeError(MARKER)):
            result = check_mx_records("example.com")
        self.assertNotIn(MARKER, _all_text(result))
        self.assertEqual(result["error"], "MX record check failed. / MXレコード確認に失敗しました。")

    def test_spf_unexpected_exception_omits_raw_detail(self) -> None:
        with self._mock_resolver(RuntimeError(MARKER)):
            result = check_spf_records("example.com")
        self.assertNotIn(MARKER, _all_text(result))
        self.assertEqual(result["error"], "SPF record check failed. / SPFレコード確認に失敗しました。")

    def test_dmarc_unexpected_exception_omits_raw_detail(self) -> None:
        with self._mock_resolver(RuntimeError(MARKER)):
            result = check_dmarc_records("example.com")
        self.assertNotIn(MARKER, _all_text(result))
        self.assertEqual(result["error"], "DMARC record check failed. / DMARCレコード確認に失敗しました。")

    def test_mx_known_dns_exception_has_no_detail_field(self) -> None:
        with self._mock_resolver(dns.resolver.NXDOMAIN()):
            result = check_mx_records("example.com")
        self.assertTrue(result["ok"])
        self.assertNotIn("detail", result)

    def test_spf_known_dns_exception_has_no_detail_field(self) -> None:
        with self._mock_resolver(dns.exception.Timeout()):
            result = check_spf_records("example.com")
        self.assertTrue(result["ok"])
        self.assertNotIn("detail", result)

    def test_dmarc_known_dns_exception_has_no_detail_field(self) -> None:
        with self._mock_resolver(dns.resolver.NoAnswer()):
            result = check_dmarc_records("example.com")
        self.assertTrue(result["ok"])
        self.assertNotIn("detail", result)


class CaaSanitizationTests(unittest.TestCase):
    def test_unexpected_exception_omits_raw_detail(self) -> None:
        resolver_instance = MagicMock()
        resolver_instance.resolve.side_effect = RuntimeError(MARKER)
        with patch(
            "network_check.checks.caa.dns.resolver.Resolver", return_value=resolver_instance
        ):
            result = check_caa("example.com")

        self.assertNotIn(MARKER, _all_text(result))
        self.assertEqual(result["error"], "CAA lookup failed. / CAA確認に失敗しました。")


class PtrSanitizationTests(unittest.TestCase):
    def test_unexpected_exception_omits_raw_detail(self) -> None:
        resolver_instance = MagicMock()
        resolver_instance.resolve.side_effect = RuntimeError(MARKER)
        with patch(
            "network_check.checks.ptr.dns.resolver.Resolver", return_value=resolver_instance
        ):
            result = check_ptr("192.0.2.1")

        self.assertNotIn(MARKER, _all_text(result))
        self.assertEqual(result["error"], "PTR lookup failed. / PTR確認に失敗しました。")


class SecurityHeadersSanitizationTests(unittest.TestCase):
    def test_unexpected_exception_omits_raw_detail(self) -> None:
        with (
            patch(
                "network_check.checks.security_headers.assert_public_connect_target",
                return_value={"ok": True, "candidates": [object()], "resolved_ips": ["203.0.113.1"]},
            ),
            patch(
                "network_check.checks.security_headers.open_validated_tcp_socket",
                side_effect=RuntimeError(MARKER),
            ),
        ):
            result = check_security_headers("https://example.com/")

        self.assertNotIn(MARKER, _all_text(result))
        self.assertEqual(result["error"], "HTTP request failed. / HTTPリクエストに失敗しました。")

    def test_invalid_input_messages_remain_specific(self) -> None:
        self.assertEqual(
            normalize_security_header_url("ftp://example.com/")["error"],
            "Only http:// and https:// URLs are supported. / http:// または https:// のURLのみ対応します。",
        )
        self.assertEqual(
            normalize_security_header_url("https://user:pass@example.com/")["error"],
            "URLs with embedded credentials are not allowed. / 認証情報を含むURLは許可しません。",
        )
        self.assertEqual(
            normalize_security_header_url("https://example.com:8443/")["error"],
            "Only default HTTP/HTTPS ports are allowed. / HTTP/HTTPSの標準ポートのみ許可します。",
        )


class DnsTimingSanitizationTests(unittest.TestCase):
    def test_unexpected_exception_omits_raw_detail(self) -> None:
        resolver_instance = MagicMock()
        resolver_instance.resolve.side_effect = RuntimeError(MARKER)
        with patch(
            "network_check.checks.dns_timing.dns.resolver.Resolver",
            return_value=resolver_instance,
        ):
            result = check_dns_timing("example.com")

        self.assertNotIn(MARKER, _all_text(result))
        self.assertEqual(
            result["a_result"]["error"], "DNS query failed. / DNS問い合わせに失敗しました。"
        )
        self.assertEqual(
            result["aaaa_result"]["error"], "DNS query failed. / DNS問い合わせに失敗しました。"
        )


class DestinationGuardSanitizationTests(unittest.TestCase):
    def test_name_resolution_failure_omits_raw_os_detail(self) -> None:
        with patch(
            "network_check.checks.destination_guard.socket.getaddrinfo",
            side_effect=socket.gaierror(-2, MARKER),
        ):
            result = resolve_public_host_for_connect("example.com", 443)

        self.assertNotIn(MARKER, _all_text(result))
        self.assertEqual(result["error"], "Name resolution failed. / 名前解決に失敗しました。")


if __name__ == "__main__":
    unittest.main()
