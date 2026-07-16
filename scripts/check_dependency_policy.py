#!/usr/bin/env python3
"""Validate the project dependency contract before authoritative work."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


POLICY = Path("docs/DEPENDENCIES.md")
REQUIRED_SECTIONS = ("## Allowed sources", "## Prohibited discovery", "## Dependency ledger")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    path = root / POLICY
    if not path.is_file():
        print(f"Dependency policy: FAIL\n- missing: {POLICY}")
        return 1
    text = path.read_text(encoding="utf-8")
    errors = [f"missing section: {section}" for section in REQUIRED_SECTIONS if section not in text]
    if not re.search(r"^- Status:\s*acknowledged\s*$", text, flags=re.MULTILINE | re.IGNORECASE):
        errors.append("policy status must be acknowledged before authoritative work")
    if "{{" in text:
        errors.append("policy contains unresolved placeholders")
    rows = re.findall(r"^\|(.+)\|\s*$", text, flags=re.MULTILINE)
    populated = []
    for row in rows:
        cells = [cell.strip() for cell in row.split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        if cells and cells[0].casefold() not in {"id", "none"}:
            populated.append(cells)
    for row in populated:
        if len(row) < 8 or any(not cell for cell in row):
            errors.append("each external dependency needs source, version, license, hash, promotion path, and approval")
            break
    if errors:
        print("Dependency policy: FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"Dependency policy: PASS ({len(populated)} promoted external dependencies)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
