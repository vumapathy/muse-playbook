#!/usr/bin/env python3
"""List recent Bland.ai calls.

Usage:
    list-calls.py [--limit N]

Prints the provider's JSON response. Useful to verify the API key works
(a fresh account returns an empty list) and to find a call_id.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import (  # noqa: E402
    add_surrogate_to_request,
    read_json_response,
)

ALLOWED_HOSTS = ("api.bland.ai", "us.api.bland.ai")
# Bland sits behind Cloudflare, which 403s non-browser clients (error 1010).
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="List recent Bland.ai calls")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    url = f"https://api.bland.ai/v1/calls?limit={args.limit}"
    request = urllib.request.Request(
        url, method="GET", headers={"User-Agent": BROWSER_UA}
    )
    add_surrogate_to_request(
        request, "custom.bland", allowed_hosts=ALLOWED_HOSTS
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as resp:
            result = read_json_response(resp)
    except Exception as exc:  # noqa: BLE001 - surface provider/network errors plainly
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
