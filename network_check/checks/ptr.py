from __future__ import annotations

import ipaddress

from typing import Any

import dns.exception
import dns.resolver
import dns.reversename

def ptr_authority_zone(parsed_ip: ipaddress._BaseAddress, reverse_name_text: str) -> str:
    labels = reverse_name_text.rstrip(".").split(".")

    if parsed_ip.version == 4:
        # First implementation: show the /24-style reverse DNS zone.
        if len(labels) >= 5 and labels[-2:] == ["in-addr", "arpa"]:
            return ".".join(labels[1:]) + "."
        return reverse_name_text

    # First implementation: show the /64-style IPv6 reverse DNS zone.
    if len(labels) >= 34 and labels[-2:] == ["ip6", "arpa"]:
        return ".".join(labels[16:]) + "."

    return reverse_name_text


def check_ptr(ip_input: str) -> dict[str, Any]:
    raw_input = ip_input.strip()

    try:
        parsed_ip = ipaddress.ip_address(raw_input)
    except ValueError:
        return {
            "ok": False,
            "ip_input": raw_input,
            "error": "Invalid IP address format. / IPアドレスの形式が正しくありません。",
        }

    resolver = dns.resolver.Resolver()
    resolver.lifetime = 3.0
    resolver.timeout = 2.0

    reverse_name = dns.reversename.from_address(str(parsed_ip))
    reverse_name_text = reverse_name.to_text()
    authority_zone = ptr_authority_zone(parsed_ip, reverse_name_text)

    try:
        answers = resolver.resolve(reverse_name, "PTR")
        ptr_records = sorted({answer.to_text() for answer in answers})
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
        ptr_records = []
    except Exception as exc:
        return {
            "ok": False,
            "ip_input": raw_input,
            "ip": str(parsed_ip),
            "ip_version": "IPv4" if parsed_ip.version == 4 else "IPv6",
            "reverse_name": reverse_name_text,
            "error": f"PTR lookup failed. / PTR確認に失敗しました: {exc}",
        }

    if ptr_records:
        level = "good"
        status = "PTR record found. / PTRレコードが見つかりました。"
    else:
        level = "warn"
        status = "No PTR record found. / PTRレコードは見つかりませんでした。"

    return {
        "ok": True,
        "ip_input": raw_input,
        "ip": str(parsed_ip),
        "ip_version": "IPv4" if parsed_ip.version == 4 else "IPv6",
        "reverse_name": reverse_name_text,
        "ptr_records": ptr_records,
        "authority_zone": authority_zone,
        "authority_note": "Estimated reverse DNS authority zone. / 推定される逆引きDNS管理ゾーンです。",
        "status": status,
        "level": level,
    }
