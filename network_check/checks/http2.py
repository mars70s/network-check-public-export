from __future__ import annotations

import os
import subprocess

from typing import Any

from .common import DOMAIN_RE, normalize_domain
from .destination_guard import assert_public_connect_target, build_blocked_target_result

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
            ["curl", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
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

        result = subprocess.run(
            ["curl", "-I", "--http2", "-s", "-o", os.devnull, "-w", "%{http_version} %{http_code} %{url_effective}", target_url],
            capture_output=True,
            text=True,
            timeout=10,
        )

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

    except Exception as exc:
        return {
            "ok": False,
            "domain": normalized,
            "error": f"HTTP/2 check failed. / HTTP/2確認に失敗しました: {exc}",
        }
