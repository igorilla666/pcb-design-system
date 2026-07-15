#!/usr/bin/env python3
"""Append a structured event to docs/PROJECT_LOG.md."""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path


def clean(value: str | None, fallback: str) -> str:
    return (value or fallback).strip().replace("\r\n", "\n")


def git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "not available"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--type", default="change", choices=["session", "change", "decision", "validation", "risk", "release"])
    parser.add_argument("--summary", required=True)
    parser.add_argument("--reason")
    parser.add_argument("--changes")
    parser.add_argument("--validation")
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--open-item", action="append", default=[])
    parser.add_argument(
        "--no-open-items",
        action="store_true",
        help="Explicitly record that no open items remain",
    )
    args = parser.parse_args()

    if args.type in {"validation", "release"} and not args.validation:
        parser.error(f"--validation is required for event type {args.type}")
    if args.no_open_items and args.open_item:
        parser.error("use either --open-item or --no-open-items")

    root = args.project.expanduser().resolve()
    log = root / "docs" / "PROJECT_LOG.md"
    if not log.is_file():
        parser.error(f"missing project log: {log}")

    timestamp = dt.datetime.now().astimezone().isoformat(timespec="minutes")
    lines = [
        "",
        f"## {timestamp} - {clean(args.summary, 'Event')}",
        "",
        f"- Type: {args.type}",
        f"- Reason: {clean(args.reason, 'not recorded')}",
        f"- Changes: {clean(args.changes, 'not recorded')}",
        f"- Validation: {clean(args.validation, 'not performed')}",
        f"- Related commit: {git_head(root)}",
    ]
    if args.source:
        lines.append("- Sources: " + "; ".join(item.strip() for item in args.source))
    if args.open_item:
        lines.append("- Open items: " + "; ".join(item.strip() for item in args.open_item))
    elif args.no_open_items:
        lines.append("- Open items: none")
    else:
        lines.append("- Open items: not assessed")

    with log.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"Appended event to {log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
