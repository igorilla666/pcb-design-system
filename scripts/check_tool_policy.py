#!/usr/bin/env python3
"""Validate which project scripts are approved for authoritative hardware work."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


MANIFEST = Path("docs/tooling-manifest.json")
TOOLS = Path("tools/pcb_design")
REQUIRED_KEYS = {"path", "purpose", "status", "sha256", "review_evidence"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    manifest_path = root / MANIFEST
    if not manifest_path.is_file():
        print(f"Tool policy: FAIL\n- missing: {MANIFEST}")
        return 1
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = data["tools"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"Tool policy: FAIL\n- invalid manifest: {exc}")
        return 1
    errors: list[str] = []
    recorded: dict[str, dict[str, object]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not REQUIRED_KEYS.issubset(entry):
            errors.append("each manifest entry needs path, purpose, status, sha256, and review_evidence")
            continue
        path = entry["path"]
        if not isinstance(path, str) or not path.startswith("tools/pcb_design/"):
            errors.append("tool paths must remain below tools/pcb_design/")
            continue
        recorded[path] = entry

    tools_root = root / TOOLS
    for tool in sorted(tools_root.rglob("*.py")) if tools_root.is_dir() else []:
        relative = tool.relative_to(root).as_posix()
        entry = recorded.get(relative)
        if entry is None:
            errors.append(f"unregistered tool: {relative}")
            continue
        if entry["sha256"] != digest(tool):
            errors.append(f"hash differs from reviewed manifest: {relative}")
        status = entry["status"]
        if relative.startswith("tools/pcb_design/legacy/") and status != "quarantined":
            errors.append(f"legacy tool must be quarantined until promoted: {relative}")
        elif not relative.startswith("tools/pcb_design/legacy/") and status != "approved":
            errors.append(f"authoritative tool is not approved: {relative}")

    for path, entry in recorded.items():
        if not (root / path).is_file():
            errors.append(f"manifest references missing tool: {path}")
        if entry.get("status") not in {"approved", "quarantined"}:
            errors.append(f"invalid tool status: {path}")
    if errors:
        print("Tool policy: FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    approved = sum(entry["status"] == "approved" for entry in recorded.values())
    quarantined = sum(entry["status"] == "quarantined" for entry in recorded.values())
    print(f"Tool policy: PASS ({approved} approved, {quarantined} quarantined)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
