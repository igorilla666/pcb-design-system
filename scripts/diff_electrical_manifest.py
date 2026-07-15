#!/usr/bin/env python3
"""Report semantic changes between two electrical manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("format") != "pcb-design-system/electrical-manifest/v1":
        raise ValueError(f"unsupported manifest: {path}")
    return data


def component_index(data: dict) -> dict[str, dict]:
    return {component["ref"]: component for component in data["components"]}


def connections(data: dict) -> set[tuple[str, str, str]]:
    return {(net["name"], node["ref"], node["pin"]) for net in data["nets"] for node in net["nodes"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--fail-on-change", action="store_true")
    args = parser.parse_args()
    try:
        before, after = load(args.before), load(args.after)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    changes: list[str] = []
    old_components, new_components = component_index(before), component_index(after)
    for ref in sorted(old_components.keys() - new_components.keys()):
        changes.append(f"component removed: {ref}")
    for ref in sorted(new_components.keys() - old_components.keys()):
        changes.append(f"component added: {ref}")
    for ref in sorted(old_components.keys() & new_components.keys()):
        for key in ("value", "footprint", "lib_id", "fields"):
            if old_components[ref].get(key) != new_components[ref].get(key):
                changes.append(f"component changed: {ref} {key}")
    old_connections, new_connections = connections(before), connections(after)
    for net, ref, pin in sorted(old_connections - new_connections):
        changes.append(f"connection removed: {net} <- {ref}.{pin}")
    for net, ref, pin in sorted(new_connections - old_connections):
        changes.append(f"connection added: {net} <- {ref}.{pin}")

    if not changes:
        print("Electrical manifest diff: no semantic changes")
        return 0
    print("Electrical manifest diff:")
    print("\n".join(f"- {change}" for change in changes))
    return 1 if args.fail_on_change else 0


if __name__ == "__main__":
    raise SystemExit(main())
