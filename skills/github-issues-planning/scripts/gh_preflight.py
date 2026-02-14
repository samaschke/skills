#!/usr/bin/env python3
"""Verify GitHub CLI availability and auth state without leaking secrets."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from typing import Any

TIMEOUT_SECONDS = 30
LOGIN_TIMEOUT_SECONDS = 300


def run(cmd: list[str], check: bool = False, timeout: int = TIMEOUT_SECONDS) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=check, timeout=timeout)


def build_result(status: str, message: str, fix: str | None = None) -> dict[str, Any]:
    return {"status": status, "message": message, "recommended_fix": fix}


def print_result(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2))
        return
    print(f"status: {payload['status']}")
    print(f"message: {payload['message']}")
    if payload.get("recommended_fix"):
        print(f"recommended_fix: {payload['recommended_fix']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check gh CLI + auth status")
    parser.add_argument("--auto-login", action="store_true", help="Run 'gh auth login' when auth is missing")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    if shutil.which("gh") is None:
        result = build_result(
            "missing-gh",
            "GitHub CLI ('gh') is not installed or not in PATH.",
            "Install gh and re-run. Then authenticate with 'gh auth login'.",
        )
        print_result(result, args.json)
        return 2

    try:
        auth = run(["gh", "auth", "status"])
    except subprocess.TimeoutExpired:
        result = build_result(
            "timeout",
            "Timed out while checking GitHub authentication.",
            "Retry `gh auth status`. If it keeps hanging, check network/proxy configuration.",
        )
        print_result(result, args.json)
        return 4

    if auth.returncode == 0:
        result = build_result("ready", "gh is installed and authenticated.")
        print_result(result, args.json)
        return 0

    if args.auto_login:
        try:
            login = subprocess.run(["gh", "auth", "login"], timeout=LOGIN_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            result = build_result(
                "timeout",
                "Timed out while running interactive login.",
                "Run `gh auth login` again and complete the prompts.",
            )
            print_result(result, args.json)
            return 4
        if login.returncode != 0:
            result = build_result(
                "auth-failed",
                "gh auth login did not complete successfully.",
                "Re-run 'gh auth login' interactively and verify with 'gh auth status'.",
            )
            print_result(result, args.json)
            return 3

        try:
            verify = run(["gh", "auth", "status"])
        except subprocess.TimeoutExpired:
            result = build_result(
                "timeout",
                "Timed out while verifying authentication after login.",
                "Retry `gh auth status`.",
            )
            print_result(result, args.json)
            return 4
        if verify.returncode == 0:
            result = build_result("ready", "gh login completed and auth is valid.")
            print_result(result, args.json)
            return 0

    result = build_result(
        "missing-auth",
        "gh is installed but not authenticated.",
        "Run 'gh auth login' (interactive) and verify with 'gh auth status'.",
    )
    print_result(result, args.json)
    return 3


if __name__ == "__main__":
    sys.exit(main())
