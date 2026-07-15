#!/usr/bin/env python3
"""Run strict KiCad ERC/DRC gates and a lightweight netlist connectivity audit."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


SKIP_PARTS = {".git", "manufacturing", "docs", "build"}


def find_cli(explicit: Path | None) -> Path:
    candidates = [explicit] if explicit else []
    found = shutil.which("kicad-cli")
    if found:
        candidates.append(Path(found))
    if sys.platform == "win32":
        candidates.extend(
            Path(f"C:/Program Files/KiCad/{version}.0/bin/kicad-cli.exe")
            for version in range(12, 7, -1)
        )
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate.resolve()
    raise RuntimeError("kicad-cli not found; install KiCad or pass --kicad-cli")


def source_files(root: Path, suffix: str) -> list[Path]:
    return sorted(
        path for path in root.rglob(f"*{suffix}")
        if path.is_file() and not any(part in SKIP_PARTS for part in path.relative_to(root).parts)
    )


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, capture_output=True, text=True)


def audit_netlist(netlist: Path) -> list[str]:
    tree = ET.parse(netlist)
    root = tree.getroot()
    connected = {
        node.get("ref", "")
        for node in root.findall("./nets/net/node")
        if node.get("ref")
    }
    failures = []
    for component in root.findall("./components/comp"):
        ref = component.get("ref", "")
        if not ref or ref.startswith("#"):
            continue
        footprint = component.findtext("footprint", default="")
        value = component.findtext("value", default="")
        mechanical = (footprint + " " + value).casefold()
        if any(name in mechanical for name in ("mountinghole", "fiducial", "toolinghole")):
            continue
        pins = component.findall("./units/unit/pins/pin")
        if ref not in connected:
            failures.append(
                f"{ref}: component has no netlist connections ({len(pins)} declared pins)"
            )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--stage", choices=["schematic", "pcb", "all"], default="all")
    parser.add_argument("--output-dir", type=Path, default=Path("build/pcb-design-check"))
    parser.add_argument("--kicad-cli", type=Path)
    args = parser.parse_args()

    root = args.project.expanduser().resolve()
    output = args.output_dir
    if not output.is_absolute():
        output = root / output
    output.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    try:
        cli = find_cli(args.kicad_cli)
        projects = source_files(root, ".kicad_pro")
        if not projects:
            raise RuntimeError("no .kicad_pro project found")

        for project_file in projects:
            stem = project_file.with_suffix("")
            label = project_file.stem
            schematic = stem.with_suffix(".kicad_sch")
            board = stem.with_suffix(".kicad_pcb")

            if args.stage in {"schematic", "all"}:
                if not schematic.is_file():
                    failures.append(f"{label}: matching .kicad_sch is missing")
                else:
                    report = output / f"{label}-erc.rpt"
                    result = run([
                        str(cli), "sch", "erc", "--output", str(report),
                        "--format", "report", "--severity-all", "--exit-code-violations",
                        str(schematic),
                    ])
                    if result.returncode != 0:
                        failures.append(f"{label}: ERC has active errors or warnings; see {report}")
                    netlist = output / f"{label}-netlist.xml"
                    exported = run([
                        str(cli), "sch", "export", "netlist", "--format", "kicadxml",
                        "--output", str(netlist), str(schematic),
                    ])
                    if exported.returncode != 0 or not netlist.is_file():
                        failures.append(f"{label}: netlist export failed")
                    else:
                        failures.extend(f"{label}: {item}" for item in audit_netlist(netlist))

            if args.stage in {"pcb", "all"}:
                if not board.is_file():
                    failures.append(f"{label}: matching .kicad_pcb is missing")
                else:
                    report = output / f"{label}-drc.rpt"
                    result = run([
                        str(cli), "pcb", "drc", "--output", str(report),
                        "--format", "report", "--severity-all", "--exit-code-violations",
                        "--schematic-parity", str(board),
                    ])
                    if result.returncode != 0:
                        failures.append(f"{label}: DRC has active errors or warnings; see {report}")
    except (OSError, RuntimeError, ET.ParseError) as exc:
        failures.append(str(exc))

    if failures:
        print("KiCad gate: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"KiCad gate: PASS ({args.stage})")
    print(f"Evidence: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
