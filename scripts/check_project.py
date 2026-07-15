#!/usr/bin/env python3
"""Validate the minimum persistent-record structure of a PCB project."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED = [
    "README.md",
    "CHANGELOG.md",
    "docs/PROJECT_STATE.md",
    "docs/PROJECT_LOG.md",
    "docs/requirements.md",
    "docs/power-budget.md",
    "docs/pin-map.md",
    "docs/component-register.csv",
    "docs/test-plan.md",
    "docs/LESSONS.md",
    "docs/RELEASE_CHECKLIST.md",
    "docs/decisions/ADR-0000-template.md",
    "hardware/README.md",
    "manufacturing/README.md",
]
PLACEHOLDERS = ("{{PROJECT_NAME}}", "{{DATE}}", "{{SYSTEM_VERSION}}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    root = args.project.expanduser().resolve()

    errors: list[str] = []
    for relative in REQUIRED:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing: {relative}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for placeholder in PLACEHOLDERS:
            if placeholder in text:
                errors.append(f"unresolved placeholder {placeholder}: {relative}")

    if not (root / ".git").exists():
        errors.append("missing Git repository (.git)")

    if errors:
        print("PCB project structure: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PCB project structure: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
