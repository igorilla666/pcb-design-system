#!/usr/bin/env python3
"""Export a compact, deterministic electrical view from a KiCad netlist.

The manifest is intended for reviews, Git diffs, and machine checks.  It is not
an alternative source of truth: KiCad schematic files and their exported
netlist remain authoritative.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


SKIP_PARTS = {".git", "manufacturing", "docs", "build"}


def find_cli() -> Path:
    found = shutil.which("kicad-cli")
    if found:
        return Path(found)
    if sys.platform == "win32":
        for version in range(12, 7, -1):
            candidate = Path(f"C:/Program Files/KiCad/{version}.0/bin/kicad-cli.exe")
            if candidate.is_file():
                return candidate
    raise RuntimeError("kicad-cli not found; pass --netlist or install KiCad")


def text(element: ET.Element | None, default: str = "") -> str:
    return element.text.strip() if element is not None and element.text else default


def fields(component: ET.Element) -> dict[str, str]:
    return {
        field.get("name", ""): text(field)
        for field in component.findall("./fields/field")
        if field.get("name")
    }


def manifest_from_netlist(netlist: Path, source: str) -> dict[str, object]:
    root = ET.parse(netlist).getroot()
    components = []
    for component in root.findall("./components/comp"):
        ref = component.get("ref", "")
        if not ref or ref.startswith("#"):
            continue
        libsource = component.find("libsource")
        components.append({
            "ref": ref,
            "value": text(component.find("value")),
            "footprint": text(component.find("footprint")),
            "lib_id": ":".join(
                part for part in (
                    libsource.get("lib", "") if libsource is not None else "",
                    libsource.get("part", "") if libsource is not None else "",
                ) if part
            ),
            "fields": fields(component),
        })

    nets = []
    for net in root.findall("./nets/net"):
        nodes = [
            {
                "ref": node.get("ref", ""),
                "pin": node.get("pin", ""),
                "pinfunction": node.get("pinfunction", ""),
                "pintype": node.get("pintype", ""),
            }
            for node in net.findall("node")
        ]
        nets.append({"name": net.get("name", ""), "nodes": sorted(nodes, key=lambda item: (item["ref"], item["pin"]))})

    components.sort(key=lambda item: item["ref"])
    nets.sort(key=lambda item: item["name"])
    connected_refs = {node["ref"] for net in nets for node in net["nodes"]}
    return {
        "format": "pcb-design-system/electrical-manifest/v1",
        "source": source,
        "summary": {
            "components": len(components),
            "nets": len(nets),
            "connected_components": len(connected_refs),
            "connections": sum(len(net["nodes"]) for net in nets),
        },
        "components": components,
        "nets": nets,
    }


def export_netlist(project_root: Path, output: Path) -> tuple[Path, str]:
    projects = sorted(
        path for path in project_root.rglob("*.kicad_pro")
        if not any(part in SKIP_PARTS for part in path.relative_to(project_root).parts)
    )
    if len(projects) != 1:
        raise RuntimeError("expected exactly one .kicad_pro outside docs/build; pass --netlist for a specific export")
    schematic = projects[0].with_suffix(".kicad_sch")
    if not schematic.is_file():
        raise RuntimeError(f"matching schematic is missing: {schematic}")
    netlist = output.with_name(f"{projects[0].stem}-netlist.xml")
    result = subprocess.run(
        [str(find_cli()), "sch", "export", "netlist", "--format", "kicadxml", "--output", str(netlist), str(schematic)],
        check=False, capture_output=True, text=True,
    )
    if result.returncode != 0 or not netlist.is_file():
        raise RuntimeError(f"netlist export failed: {result.stderr.strip() or result.stdout.strip()}")
    return netlist, projects[0].name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", type=Path, help="KiCad project root (exports its netlist)")
    parser.add_argument("--netlist", type=Path, help="Existing KiCad XML netlist; avoids invoking KiCad")
    parser.add_argument("--output", type=Path, default=Path("build/pcb-design-check/electrical-manifest.json"))
    args = parser.parse_args()
    if bool(args.project) == bool(args.netlist):
        parser.error("pass exactly one of project or --netlist")

    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        if args.netlist:
            netlist = args.netlist.expanduser().resolve()
            if not netlist.is_file():
                raise RuntimeError(f"netlist is missing: {netlist}")
            source = netlist.name
        else:
            netlist, source = export_netlist(args.project.expanduser().resolve(), output)
        data = manifest_from_netlist(netlist, source)
        output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (ET.ParseError, OSError, RuntimeError) as exc:
        print(f"Electrical manifest: FAIL\n- {exc}", file=sys.stderr)
        return 1
    print(f"Electrical manifest: {output}")
    print("Summary: " + ", ".join(f"{key}={value}" for key, value in data["summary"].items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
