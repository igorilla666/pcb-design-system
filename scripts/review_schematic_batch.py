#!/usr/bin/env python3
"""Run the schematic gate and emit one compact, deterministic review report."""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def run(command: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=root, check=False, capture_output=True, text=True)


def relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--baseline", type=Path, help="Prior electrical manifest to compare")
    parser.add_argument("--output-dir", type=Path, default=Path("build/pcb-design-check"))
    parser.add_argument("--fail-on-change", action="store_true", help="Fail when the baseline differs")
    args = parser.parse_args()

    root = args.project.expanduser().resolve()
    output = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    manifest = output / "electrical-manifest.json"
    gate = run([sys.executable, str(SCRIPT_DIR / "check_kicad.py"), ".", "--stage", "schematic", "--output-dir", str(output)], root)
    exported = run([sys.executable, str(SCRIPT_DIR / "export_electrical_manifest.py"), ".", "--output", str(manifest)], root)

    diff = None
    if args.baseline:
        baseline = args.baseline if args.baseline.is_absolute() else root / args.baseline
        command = [sys.executable, str(SCRIPT_DIR / "diff_electrical_manifest.py"), str(baseline), str(manifest)]
        if args.fail_on_change:
            command.append("--fail-on-change")
        diff = run(command, root)

    passed = gate.returncode == 0 and exported.returncode == 0 and (diff is None or diff.returncode == 0)
    sections = [
        "# Schematic review batch",
        "",
        f"- Timestamp: {dt.datetime.now().astimezone().isoformat(timespec='minutes')}",
        f"- Result: {'PASS' if passed else 'FAIL'}",
        f"- Manifest: `{relative(root, manifest)}`",
        "",
        "## ERC and netlist gate",
        "",
        "```text",
        (gate.stdout + gate.stderr).strip() or "no output",
        "```",
        "",
        "## Manifest export",
        "",
        "```text",
        (exported.stdout + exported.stderr).strip() or "no output",
        "```",
    ]
    if diff is not None:
        sections.extend([
            "",
            "## Baseline diff",
            "",
            "```text",
            (diff.stdout + diff.stderr).strip() or "no output",
            "```",
        ])
    report = output / "schematic-review.md"
    report.write_text("\n".join(sections) + "\n", encoding="utf-8")
    print(f"Schematic review batch: {'PASS' if passed else 'FAIL'}")
    print(f"Report: {report}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
