#!/usr/bin/env python3
"""Create typed GitHub issues with priority and optional parent linkage."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TIMEOUT_SECONDS = 30
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")

TYPE_LABELS = {
    "epic": "type/epic",
    "story": "type/story",
    "bug": "type/bug",
    "finding": "type/finding",
    "work-item": "type/work-item",
}

PRIORITY_LABELS = {"p0": "priority/p0", "p1": "priority/p1", "p2": "priority/p2", "p3": "priority/p3"}


def read_body(args: argparse.Namespace) -> str:
    if args.body_file:
        return Path(args.body_file).read_text(encoding="utf-8").strip()
    if args.body:
        return args.body.strip()
    return ""


def compose_body(base_body: str, issue_type: str, priority: str, parent: int | None) -> str:
    lines: list[str] = []
    if base_body:
        lines.append(base_body)
    lines.extend(
        [
            "",
            "## Tracking",
            f"- Type: {issue_type}",
            f"- Priority: {priority}",
        ]
    )
    if parent is not None:
        lines.append(f"- Parent: #{parent}")
        lines.append("")
        lines.append(f"Parent: #{parent}")
    return "\n".join(lines).strip()


def ensure_auth() -> None:
    try:
        result = subprocess.run(["gh", "auth", "status"], text=True, capture_output=True, timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        print("Timed out checking `gh auth status`. Please retry.", file=sys.stderr)
        sys.exit(4)
    if result.returncode != 0:
        print("gh auth is missing. Run 'gh auth login' first.", file=sys.stderr)
        sys.exit(3)


def validate_repo(repo: str) -> str:
    normalized = repo.strip()
    if not REPO_RE.fullmatch(normalized):
        print("Invalid --repo format. Expected owner/repo.", file=sys.stderr)
        sys.exit(2)
    return normalized


def resolve_repo(explicit_repo: str | None) -> str:
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
        print("Timed out resolving current repository. Provide --repo <owner/repo>.", file=sys.stderr)
        sys.exit(4)
    if result.returncode == 0:
        resolved = result.stdout.strip()
        if resolved:
            return validate_repo(resolved)

    print(
        "Could not resolve default repository from current directory. "
        "Provide --repo <owner/repo>.",
        file=sys.stderr,
    )
    sys.exit(2)


def build_command(args: argparse.Namespace, body: str, repo: str) -> list[str]:
    labels = [TYPE_LABELS[args.type], PRIORITY_LABELS[args.priority], *args.label]
    deduped_labels = list(dict.fromkeys(labels))

    cmd = [
        "gh",
        "issue",
        "create",
        "--repo",
        repo,
        "--title",
        args.title,
        "--body",
        body,
    ]

    for label in deduped_labels:
        cmd.extend(["--label", label])
    for assignee in args.assignee:
        cmd.extend(["--assignee", assignee])

    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a typed GitHub issue")
    parser.add_argument("--repo", help="owner/repo; defaults to current git upstream repo")
    parser.add_argument("--type", choices=sorted(TYPE_LABELS.keys()), required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body")
    parser.add_argument("--body-file")
    parser.add_argument("--priority", choices=sorted(PRIORITY_LABELS.keys()), required=True)
    parser.add_argument("--parent", type=int)
    parser.add_argument("--assignee", action="append", default=[])
    parser.add_argument("--label", action="append", default=[], help="Extra labels")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.body and args.body_file:
        print("Use either --body or --body-file, not both.", file=sys.stderr)
        return 2

    repo = resolve_repo(args.repo)
    body = compose_body(read_body(args), args.type, args.priority, args.parent)
    cmd = build_command(args, body, repo)

    if args.dry_run:
        print(
            json.dumps(
                {
                    "mode": "dry-run",
                    "repo": repo,
                    "type": args.type,
                    "priority": args.priority,
                    "parent": args.parent,
                    "command": cmd,
                    "body": body,
                },
                indent=2,
            )
        )
        return 0

    ensure_auth()
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        print("Timed out while creating issue. Retry the command.", file=sys.stderr)
        return 4
    if result.returncode != 0:
        print(result.stderr.strip() or "Failed to create issue.", file=sys.stderr)
        return result.returncode

    print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
