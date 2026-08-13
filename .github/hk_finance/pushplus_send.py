#!/usr/bin/env python3
"""Send an HTML file to PushPlus (WeChat)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests

PUSHPLUS_URL = "https://www.pushplus.plus/send"


def main() -> int:
    parser = argparse.ArgumentParser(description="Push an HTML briefing via PushPlus")
    parser.add_argument("html_path", help="Path to HTML content file")
    parser.add_argument(
        "--title",
        default="章鱼AI｜港股财经简报",
        help="PushPlus message title",
    )
    parser.add_argument(
        "--topic",
        default="",
        help="Optional PushPlus topic / group code",
    )
    args = parser.parse_args()

    token = os.environ.get("PUSHPLUS_TOKEN", "").strip()
    if not token:
        print("ERROR: PUSHPLUS_TOKEN is not set", file=sys.stderr)
        return 2

    html_path = Path(args.html_path)
    if not html_path.is_file():
        print(f"ERROR: HTML file not found: {html_path}", file=sys.stderr)
        return 2

    content = html_path.read_text(encoding="utf-8")
    payload = {
        "token": token,
        "title": args.title,
        "content": content,
        "template": "html",
    }
    if args.topic:
        payload["topic"] = args.topic

    resp = requests.post(PUSHPLUS_URL, json=payload, timeout=30)
    print("HTTP", resp.status_code)
    print(resp.text)

    try:
        data = resp.json()
    except json.JSONDecodeError:
        print("ERROR: PushPlus returned non-JSON", file=sys.stderr)
        return 1

    # PushPlus uses code == 200 for success
    if resp.status_code != 200 or data.get("code") not in (200, "200"):
        print(f"ERROR: PushPlus failed: {data}", file=sys.stderr)
        return 1

    print("✅ PushPlus sent:", data.get("msg", "ok"), "data=", data.get("data"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
