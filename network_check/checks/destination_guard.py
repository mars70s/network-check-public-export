from __future__ import annotations

import ipaddress
import socket

from typing import Any


LOCAL_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "ip6-localhost",
    "ip6-loopback",
}


def is_disallowed_target_ip(ip_text: str) -> bool:
    try:
        parsed = ipaddress.ip_address(ip_text)
    except ValueError:
        return True

    return (
        not parsed.is_global
        or parsed.is_private
        or parsed.is_loopback
        or parsed.is_link_local
        or parsed.is_multicast
        or parsed.is_unspecified
        or parsed.is_reserved
    )


def normalize_connect_host(host_input: str) -> dict[str, Any]:
    if not isinstance(host_input, str):
        return {
            "ok": False,
            "host": "",
            "error": "Host is required. / ホスト名を入力してください。",
        }

    raw_host = host_input.strip().rstrip(".")

    if not raw_host:
        return {
            "ok": False,
            "host": raw_host,
            "error": "Host is required. / ホスト名を入力してください。",
        }

    if raw_host.lower() in LOCAL_HOSTNAMES:
        return {
            "ok": False,
            "host": raw_host.lower(),
            "error": "Localhost targets are not allowed. / localhost 宛先は許可しません。",
        }

    try:
        ip_literal = ipaddress.ip_address(raw_host)
    except ValueError:
        try:
            normalized_host = raw_host.encode("idna").decode("ascii").lower()
        except UnicodeError:
            return {
                "ok": False,
                "host": raw_host,
                "error": "Invalid hostname. / ホスト名の形式が正しくありません。",
            }

        if normalized_host.lower() in LOCAL_HOSTNAMES:
            return {
                "ok": False,
                "host": normalized_host.lower(),
                "error": "Localhost targets are not allowed. / localhost 宛先は許可しません。",
            }

        return {
            "ok": True,
            "host": normalized_host,
            "is_ip_literal": False,
        }

    normalized_ip = str(ip_literal)
    if is_disallowed_target_ip(normalized_ip):
        return {
            "ok": False,
            "host": normalized_ip,
            "is_ip_literal": True,
            "resolved_ips": [normalized_ip],
            "blocked_ips": [normalized_ip],
            "error": "Target is not a public address. / 対象が公開用IPアドレスではありません。",
        }

    return {
        "ok": True,
        "host": normalized_ip,
        "is_ip_literal": True,
        "resolved_ips": [normalized_ip],
    }


def resolve_public_host_for_connect(host_input: str, port: int) -> dict[str, Any]:
    if not isinstance(port, int) or port < 1 or port > 65535:
        return {
            "ok": False,
            "host": host_input,
            "port": port,
            "error": "Invalid port number. / ポート番号の形式が正しくありません。",
        }

    normalized = normalize_connect_host(host_input)
    if not normalized["ok"]:
        result = dict(normalized)
        result["port"] = port
        return result

    if normalized.get("is_ip_literal"):
        return {
            "ok": True,
            "host": normalized["host"],
            "port": port,
            "resolved_ips": normalized.get("resolved_ips", [normalized["host"]]),
        }

    host = normalized["host"]

    try:
        addrinfo = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        return {
            "ok": False,
            "host": host,
            "port": port,
            "error": f"Name resolution failed. / 名前解決に失敗しました: {exc}",
        }

    resolved_ips = sorted({item[4][0] for item in addrinfo})

    if not resolved_ips:
        return {
            "ok": False,
            "host": host,
            "port": port,
            "resolved_ips": [],
            "error": "No target address was resolved. / 宛先IPアドレスが解決できませんでした。",
        }

    blocked_ips = [ip for ip in resolved_ips if is_disallowed_target_ip(ip)]
    if blocked_ips:
        return {
            "ok": False,
            "host": host,
            "port": port,
            "resolved_ips": resolved_ips,
            "blocked_ips": blocked_ips,
            "error": "Target resolves to a non-public address. / 対象ホストが公開用ではないIPアドレスへ解決されました。",
        }

    return {
        "ok": True,
        "host": host,
        "port": port,
        "resolved_ips": resolved_ips,
    }


def assert_public_connect_target(host_input: str, port: int) -> dict[str, Any]:
    return resolve_public_host_for_connect(host_input, port)


def build_blocked_target_result(domain: str, guard_result: dict[str, Any], check_label: str) -> dict[str, Any]:
    return {
        "ok": False,
        "domain": domain,
        "guard": "destination_safety",
        "check": check_label,
        "error": guard_result.get(
            "error",
            "Target is not allowed. / この宛先は許可されていません。",
        ),
    }
