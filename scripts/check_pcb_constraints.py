#!/usr/bin/env python3
"""Validate modular pre-placement PCB constraints without loading all details into one file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


INDEX = Path("docs/pcb-constraints/index.json")
PCB_LAYOUT = Path("docs/pcb-layout.json")
REQUIRED = {"mechanical", "manufacturing", "netclasses", "ground", "zones", "routing", "power-thermal", "assembly-test"}
MODULE_KEYS = {
    "mechanical": {"outline_mm", "cutouts_mm", "mounting_holes", "connector_access", "height_limits_mm"},
    "manufacturing": {"stackup", "fabricator_capabilities"},
    "netclasses": {"classes", "net_assignments"},
    "ground": {"reference_layers", "domains", "continuous_plane_rules", "blocked_areas", "return_path_review"},
    "zones": {"functional_zones", "isolation_boundaries"},
    "routing": {"preferred_layers", "via_policy", "critical_nets"},
    "power-thermal": {"power_paths", "thermal_constraints"},
    "assembly-test": {"fiducials", "test_points", "programming_access", "orientation_rules"},
}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("root must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--require-placement-ready", action="store_true")
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    errors: list[str] = []
    try:
        layout = load(root / PCB_LAYOUT)
        if layout.get("format") != "pcb-design-system/pcb-layout/v2":
            errors.append("pcb-layout.json must use pcb-layout/v2")
        if layout.get("constraints_index") != INDEX.as_posix():
            errors.append(f"pcb-layout.json must reference {INDEX.as_posix()}")
        if layout.get("board_source", {}).get("mode") != "update-from-schematic":
            errors.append("board source must be update-from-schematic")
        index = load(root / INDEX)
        if index.get("format") != "pcb-design-system/pcb-constraints-index/v1":
            errors.append("invalid PCB constraints index format")
        modules = index.get("modules")
        if not isinstance(modules, list):
            raise ValueError("constraints index modules must be a list")
        found: set[str] = set()
        for entry in modules:
            if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not isinstance(entry.get("path"), str):
                errors.append("each constraint index entry needs id and path")
                continue
            module_id, relpath = entry["id"], entry["path"]
            found.add(module_id)
            if module_id not in MODULE_KEYS:
                errors.append(f"unknown constraint module: {module_id}")
                continue
            path = root / relpath
            try:
                module = load(path)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"cannot read {module_id}: {exc}")
                continue
            if module.get("format") != f"pcb-design-system/pcb-constraint-{module_id}/v1":
                errors.append(f"invalid format: {relpath}")
            status = module.get("status")
            if status not in {"planned", "accepted"}:
                errors.append(f"invalid status: {relpath}")
            if args.require_placement_ready:
                if status != "accepted":
                    errors.append(f"constraint not accepted: {module_id}")
                summary = module.get("decision_summary")
                if not isinstance(summary, str) or not summary.strip():
                    errors.append(f"{module_id} lacks a decision_summary (state N/A decisions explicitly)")
            missing_keys = MODULE_KEYS[module_id] - set(module)
            if missing_keys:
                errors.append(f"{module_id} is missing fields: " + ", ".join(sorted(missing_keys)))
        missing = REQUIRED - found
        if missing:
            errors.append("missing constraint modules: " + ", ".join(sorted(missing)))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
    if errors:
        print("PCB constraints: FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    state = "placement-ready" if args.require_placement_ready else "planned"
    print(f"PCB constraints: PASS ({state}; modules={len(REQUIRED)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
