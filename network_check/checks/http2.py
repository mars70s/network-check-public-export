from __future__ import annotations

import ipaddress
import os
import subprocess

from typing import Any

from .common import DOMAIN_RE, normalize_domain
from .destination_guard import assert_public_connect_target, build_blocked_target_result

HTTP2_CAPABILITY_TIMEOUT = 5.0
HTTP2_CANDIDATE_TIMEOUT = 10.0


def build_curl_resolve_entry(host: str, port: int, ip_text: str) -> str:
    parsed_ip = ipaddress.ip_address(ip_text)
    address = f"[{parsed_ip}]" if parsed_ip.version == 6 else str(parsed_ip)
    return f"{host}:{port}:{address}"

def check_http2(domain: str) -> dict[str, Any]:
    normalized = normalize_domain(domain)

    if not normalized or not DOMAIN_RE.match(normalized + "."):
        return {
            "ok": False,
            "domain": normalized,
            "error": "Invalid domain format. / ドメイン名の形式が正しくありません。",
        }

    guard_result = assert_public_connect_target(normalized, 443)
    if not guard_result["ok"]:
        return build_blocked_target_result(normalized, guard_result, "http2")

    try:
        version_result = subprocess.run(
            ["curl", "--disable", "--version"],
            capture_output=True,
            text=True,
            timeout=HTTP2_CAPABILITY_TIMEOUT,
        )

        if "HTTP2" not in version_result.stdout:
            return {
                "ok": True,
                "domain": normalized,
                "available": False,
                "status": "HTTP/2 check unavailable on this runtime. / この実行環境ではHTTP/2確認を利用できません。",
                "level": "warn",
            }

        target_url = f"https://{normalized}/"
        result = None
        last_error: Exception | None = None
        attempted_ips: set[str] = set()

        for candidate in guard_result["candidates"]:
            if candidate.ip in attempted_ips:
                continue
            attempted_ips.add(candidate.ip)

            resolve_entry = build_curl_resolve_entry(normalized, 443, candidate.ip)
            try:
                candidate_result = subprocess.run(
                    [
                        "curl",
                        "--disable",
                        "-I",
                        "--http2",
                        "--resolve",
                        resolve_entry,
                        "--noproxy",
                        "*",
                        "-s",
                        "-o",
                        os.devnull,
                        "-w",
                        "%{http_version} %{http_code} %{url_effective}",
                        target_url,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=HTTP2_CANDIDATE_TIMEOUT,
                )
            except Exception as exc:
                last_error = exc
                continue

            result = candidate_result
            if candidate_result.returncode == 0:
                break

        if result is None:
            if last_error is not None:
                raise last_error
            raise OSError("No validated connection candidates are available.")

        output = result.stdout.strip()
        parts = output.split(" ", 2)

        http_version = parts[0] if len(parts) > 0 else "unknown"
        status_code = parts[1] if len(parts) > 1 else "unknown"
        final_url = parts[2] if len(parts) > 2 else target_url

        if http_version == "2":
            level = "good"
            status = "HTTP/2 negotiated. / HTTP/2で接続されました。"
        else:
            level = "warn"
            status = "HTTP/2 was not negotiated. / HTTP/2では接続されませんでした。"

        return {
            "ok": True,
            "available": True,
            "domain": normalized,
            "http_version": http_version,
            "status_code": status_code,
            "final_url": final_url,
            "status": status,
            "level": level,
        }

    except Exception:
        return {
            "ok": False,
            "domain": normalized,
            "error": "HTTP/2 check failed. / HTTP/2確認に失敗しました。",
        }
