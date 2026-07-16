#!/usr/bin/env python3
"""Validate the recorded visual-layout plan for an authoritative schematic."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PLAN = Path("docs/schematic-layout.md")
REQUIRED_SECTIONS = ("## Sheet and reading flow", "## Functional blocks", "## Visual review")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    path = root / PLAN
    if not path.is_file():
        print(f"Schematic layout plan: FAIL\n- missing: {PLAN}")
        return 1
    text = path.read_text(encoding="utf-8")
    errors = [f"missing section: {section}" for section in REQUIRED_SECTIONS if section not in text]
    if not re.search(r"^- Status:\s*accepted\s*$", text, flags=re.MULTILINE | re.IGNORECASE):
        errors.append("layout plan status must be accepted after visual review")
    block_rows = []
    for row in re.findall(r"^\|(.+)\|\s*$", text, flags=re.MULTILINE):
        cells = [cell.strip() for cell in row.split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        if all(cells):
            block_rows.append(cells)
    if len(block_rows) < 2:  # Header plus at least one populated functional block.
        errors.append("functional-block table needs at least one populated block")
    review_items = re.findall(r"^- \[x\] .+", text, flags=re.MULTILINE | re.IGNORECASE)
    if len(review_items) < 3:
        errors.append("record at least three completed visual-review checks")
    if errors:
        print("Schematic layout plan: FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Schematic layout plan: PASS")
    print(f"Evidence: {PLAN}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
