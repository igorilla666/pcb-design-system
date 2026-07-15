#!/usr/bin/env python3
"""Validate PCB project records and portability files, not electrical design."""

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
PORTABILITY_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "tools/pcb_design/SYSTEM_VERSION",
    "tools/pcb_design/check_project.py",
    "tools/pcb_design/check_kicad.py",
    "tools/pcb_design/record_event.py",
    "tools/pcb_design/snapshot_project.py",
]
PLACEHOLDERS = (
    "{{PROJECT_NAME}}",
    "{{DATE}}",
    "{{SYSTEM_VERSION}}",
    "{{REPOSITORY_URL}}",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat missing multi-agent portability files as errors",
    )
    args = parser.parse_args()
    root = args.project.expanduser().resolve()

    errors: list[str] = []
    warnings: list[str] = []
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

    for relative in PORTABILITY_FILES:
        if not (root / relative).is_file():
            message = f"missing portability file: {relative}"
            if args.strict:
                errors.append(message)
            else:
                warnings.append(message)

    if errors:
        print("PCB project record structure: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    if warnings:
        print("PCB project record structure: PASS WITH WARNINGS")
        for warning in warnings:
            print(f"- {warning}")
        return 0

    print("PCB project record structure: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
