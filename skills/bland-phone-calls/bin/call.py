#!/usr/bin/env python3
"""Place an outbound AI phone call via Bland.ai.

Usage:
    call.py <phone_number> <task> [--first-sentence TEXT] [--voice NAME] [--no-record]

Prints the provider's JSON response (includes call_id on success).
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
API_URL = "https://api.bland.ai/v1/calls"
# Bland sits behind Cloudflare, which 403s non-browser clients (error 1010).
# A browser User-Agent is required on every request.
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Place an outbound Bland.ai call")
    parser.add_argument("phone_number", help="Destination in E.164 format, e.g. +15550123456")
    parser.add_argument("task", help="Prompt telling the AI the call objective and behavior")
    parser.add_argument("--first-sentence", default=None)
    parser.add_argument("--voice", default=None)
    parser.add_argument("--no-record", action="store_true", help="Disable call recording")
    args = parser.parse_args()

    body: dict = {
        "phone_number": args.phone_number,
        "task": args.task,
        "record": not args.no_record,
    }
    if args.first_sentence:
        body["first_sentence"] = args.first_sentence
    if args.voice:
        body["voice"] = args.voice

    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": BROWSER_UA},
        method="POST",
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
