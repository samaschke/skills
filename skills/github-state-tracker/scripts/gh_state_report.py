#!/usr/bin/env python3
"""Generate normalized GitHub issue snapshots and markdown reports."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

TYPE_PREFIX = "type/"
PRIORITY_PREFIX = "priority/"
PARENT_RE = re.compile(r"(?im)^parent:\s*#(\d+)\s*$")
PRIORITY_ORDER = {"p0": 0, "p1": 1, "p2": 2, "p3": 3, "unprioritized": 99}
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
TIMEOUT_SECONDS = 30


def validate_repo(repo: str) -> str:
    normalized = repo.strip()
    if not REPO_RE.fullmatch(normalized):
        raise ValueError("Invalid --repo format. Expected owner/repo.")
    return normalized


def resolve_repo(explicit_repo: str | None) -> str | None:
    if explicit_repo:
        return validate_repo(explicit_repo)

    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
            text=True,
            capture_output=True,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return None
    if result.returncode == 0:
        resolved = result.stdout.strip()
        if resolved:
            try:
                return validate_repo(resolved)
            except ValueError:
                return None

    return None


def run_gh_issue_list(repo: str, state: str, limit: int) -> list[dict[str, Any]]:
    cmd = [
        "gh",
        "issue",
        "list",
        "--repo",
        repo,
        "--state",
        state,
        "--limit",
        str(limit),
        "--json",
        "number,title,state,labels,assignees,createdAt,updatedAt,closedAt,body,url",
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, timeout=TIMEOUT_SECONDS)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "gh issue list failed")
    return json.loads(result.stdout)


def extract_label(labels: list[dict[str, Any]], prefix: str, fallback: str) -> str:
    for label in labels:
        name = str(label.get("name", ""))
        if name.startswith(prefix):
            return name.removeprefix(prefix)
    return fallback


def normalize_issue(item: dict[str, Any]) -> dict[str, Any]:
    labels = item.get("labels") or []
    body = item.get("body") or ""
    parent_match = PARENT_RE.search(body)
    parent = int(parent_match.group(1)) if parent_match else None

    issue_type = extract_label(labels, TYPE_PREFIX, "untyped")
    priority = extract_label(labels, PRIORITY_PREFIX, "unprioritized")

    return {
        "number": item.get("number"),
        "title": item.get("title"),
        "url": item.get("url"),
        "state": (item.get("state") or "").lower(),
        "type": issue_type,
        "priority": priority,
        "parent": parent,
        "assignees": [a.get("login") for a in (item.get("assignees") or []) if a.get("login")],
        "createdAt": item.get("createdAt"),
        "updatedAt": item.get("updatedAt"),
        "closedAt": item.get("closedAt"),
    }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_delta(previous: list[dict[str, Any]], current: list[dict[str, Any]]) -> dict[str, Any]:
    prev_by_number = {int(i["number"]): i for i in previous if i.get("number") is not None}
    curr_by_number = {int(i["number"]): i for i in current if i.get("number") is not None}

    new_items = sorted(n for n in curr_by_number if n not in prev_by_number)
    closed_items = sorted(
        n
        for n, curr in curr_by_number.items()
        if n in prev_by_number and prev_by_number[n].get("state") != "closed" and curr.get("state") == "closed"
    )
    changed_items = sorted(
        n
        for n, curr in curr_by_number.items()
        if n in prev_by_number and prev_by_number[n].get("updatedAt") != curr.get("updatedAt")
    )

    return {
        "new": new_items,
        "closed": closed_items,
        "changed": changed_items,
        "counts": {
            "new": len(new_items),
            "closed": len(closed_items),
            "changed": len(changed_items),
        },
    }


def build_report(repo: str, snapshot_at: str, issues: list[dict[str, Any]], delta: dict[str, Any]) -> str:
    def escape_md_cell(value: Any) -> str:
        text = str(value or "")
        text = text.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").replace("\r", " ").strip()
        return text

    by_state = Counter(i["state"] for i in issues)
    by_type = Counter(i["type"] for i in issues)
    by_priority = Counter(i["priority"] for i in issues)

    open_items = [i for i in issues if i["state"] != "closed"]
    open_items.sort(key=lambda x: (PRIORITY_ORDER.get(x["priority"], 99), x.get("number") or 0))

    lines = [
        f"# GitHub Issue State Report ({repo})",
        "",
        f"Snapshot: `{snapshot_at}`",
        "",
        "## Totals",
        f"- Total issues: {len(issues)}",
        f"- Open: {by_state.get('open', 0)}",
        f"- Closed: {by_state.get('closed', 0)}",
        "",
        "## By Type",
    ]

    for key in sorted(by_type):
        lines.append(f"- {escape_md_cell(key)}: {by_type[key]}")

    lines.extend(["", "## By Priority"])
    for key in sorted(by_priority, key=lambda k: PRIORITY_ORDER.get(k, 99)):
        lines.append(f"- {escape_md_cell(key)}: {by_priority[key]}")

    lines.extend(
        [
            "",
            "## Delta",
            f"- New: {delta['counts']['new']}",
            f"- Closed: {delta['counts']['closed']}",
            f"- Changed: {delta['counts']['changed']}",
            "",
            "## Top Open Priorities",
            "| Priority | Type | Issue | Parent | Title |",
            "| --- | --- | --- | --- | --- |",
        ]
    )

    for issue in open_items[:20]:
        parent = f"#{issue['parent']}" if issue.get("parent") else "-"
        issue_number = issue.get("number")
        issue_url = str(issue.get("url") or "").strip()
        issue_ref = f"[#{issue_number}]({issue_url})" if issue_url else f"#{issue_number}"
        safe_priority = escape_md_cell(issue.get("priority"))
        safe_type = escape_md_cell(issue.get("type"))
        safe_parent = escape_md_cell(parent)
        safe_title = escape_md_cell(issue.get("title"))
        lines.append(
            f"| {safe_priority} | {safe_type} | {issue_ref} | {safe_parent} | {safe_title} |"
        )

    return "\n".join(lines) + "\n"


def resolve_previous_snapshot(snapshot_dir: Path | None) -> list[dict[str, Any]]:
    if not snapshot_dir:
        return []
    latest = snapshot_dir / "latest.json"
    if not latest.exists():
        return []
    payload = load_json(latest)
    return payload.get("issues", [])


def main() -> int:
    parser = argparse.ArgumentParser(description="Create GitHub issue state snapshot + report")
    parser.add_argument("--repo", help="owner/repo")
    parser.add_argument("--state", choices=["open", "closed", "all"], default="all")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--input-json", help="Read raw issue list JSON from file (test mode)")
    parser.add_argument("--previous-json", help="Previous normalized snapshot JSON")
    parser.add_argument("--snapshot-dir", help="Directory for timestamped snapshots and latest.json")
    parser.add_argument("--output-json", help="Write normalized JSON payload")
    parser.add_argument("--output-md", help="Write markdown report")
    args = parser.parse_args()

    try:
        repo = resolve_repo(args.repo) if not args.input_json else args.repo
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if not args.input_json and not repo:
        print(
            "Could not resolve repository from current directory. "
            "Provide --repo <owner/repo> or run from a GitHub repo checkout.",
            file=sys.stderr,
        )
        return 2

    try:
        raw_issues = load_json(Path(args.input_json)) if args.input_json else run_gh_issue_list(repo, args.state, args.limit)
    except (subprocess.TimeoutExpired, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        return 3

    normalized = [normalize_issue(i) for i in raw_issues]
    snapshot_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    previous_issues: list[dict[str, Any]]
    if args.previous_json:
        previous_payload = load_json(Path(args.previous_json))
        previous_issues = previous_payload.get("issues", [])
    else:
        previous_issues = resolve_previous_snapshot(Path(args.snapshot_dir)) if args.snapshot_dir else []

    delta = build_delta(previous_issues, normalized)

    payload = {
        "repo": repo or "input-json",
        "snapshotAt": snapshot_at,
        "issues": normalized,
        "delta": delta,
    }

    if args.snapshot_dir:
        snapshot_dir = Path(args.snapshot_dir)
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        save_json(snapshot_dir / f"snapshot-{timestamp}.json", payload)
        save_json(snapshot_dir / "latest.json", payload)

    if args.output_json:
        save_json(Path(args.output_json), payload)
    else:
        print(json.dumps(payload, indent=2))

    if args.output_md:
        report = build_report(repo or "input-json", snapshot_at, normalized, delta)
        report_path = Path(args.output_md)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
