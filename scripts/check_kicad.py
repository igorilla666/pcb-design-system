#!/usr/bin/env python3
"""Run strict KiCad ERC/DRC gates and a lightweight netlist connectivity audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


SKIP_PARTS = {".git", "manufacturing", "docs", "build"}
TOOLCHAIN_FILE = Path("docs/kicad-toolchain.json")


def find_cli(explicit: Path | None, configured_major: int) -> Path:
    """Find only the CLI for the declared major; never fall back to another one."""
    candidates = [explicit] if explicit else []
    found = shutil.which("kicad-cli")
    if found:
        candidates.append(Path(found))
    if sys.platform == "win32":
        candidates.append(Path(f"C:/Program Files/KiCad/{configured_major}.0/bin/kicad-cli.exe"))

    inspected: list[str] = []
    for candidate in candidates:
        if not candidate or not candidate.is_file():
            continue
        resolved = candidate.resolve()
        actual_major = cli_major(resolved)
        inspected.append(f"{resolved} (major {actual_major})")
        if actual_major == configured_major:
            return resolved
    details = "; ".join(inspected) or "no usable kicad-cli found"
    raise RuntimeError(
        f"KiCad {configured_major} CLI is required by {TOOLCHAIN_FILE}; do not fall back to a "
        f"different major. Inspected: {details}"
    )


def source_files(root: Path, suffix: str) -> list[Path]:
    return sorted(
        path for path in root.rglob(f"*{suffix}")
        if path.is_file() and not any(part in SKIP_PARTS for part in path.relative_to(root).parts)
    )


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, capture_output=True, text=True)


def cli_major(cli: Path) -> int:
    result = run([str(cli), "--version"])
    match = re.search(r"\b(\d+)\.\d+(?:\.\d+)?\b", result.stdout + result.stderr)
    if result.returncode != 0 or not match:
        raise RuntimeError(f"cannot determine KiCad CLI version: {result.stderr.strip() or result.stdout.strip()}")
    return int(match.group(1))


def required_major(root: Path) -> int:
    path = root / TOOLCHAIN_FILE
    if not path.is_file():
        raise RuntimeError(f"missing KiCad toolchain declaration: {TOOLCHAIN_FILE}")
    try:
        value = json.loads(path.read_text(encoding="utf-8")).get("required_major")
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid KiCad toolchain declaration: {exc}") from exc
    if not isinstance(value, int) or value < 1:
        raise RuntimeError(f"{TOOLCHAIN_FILE} must set a positive integer required_major")
    return value


def schematic_generator_major(schematic: Path) -> int | None:
    try:
        header = schematic.read_text(encoding="utf-8")[:4096]
    except OSError as exc:
        raise RuntimeError(f"cannot read {schematic}: {exc}") from exc
    match = re.search(r'\(generator_version\s+"(\d+)\.', header)
    return int(match.group(1)) if match else None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def migration_probe(cli: Path, kind: str, source: Path, output: Path) -> str | None:
    """Fail when KiCad would upgrade a disposable copy of an authoritative file."""
    probe = output / f"{source.stem}-{kind}-migration-probe{source.suffix}"
    shutil.copy2(source, probe)
    result = run([str(cli), kind, "upgrade", str(probe)])
    original_hash = sha256(source)
    probe_hash = sha256(probe) if probe.is_file() else "missing"
    evidence = output / f"{source.stem}-{kind}-migration.txt"
    evidence.write_text(
        "KiCad migration probe\n"
        f"Source: {source}\n"
        f"CLI exit code: {result.returncode}\n"
        f"Source SHA-256: {original_hash}\n"
        f"Probe SHA-256: {probe_hash}\n"
        f"CLI output: {(result.stdout + result.stderr).strip() or 'none'}\n",
        encoding="utf-8",
    )
    probe.unlink(missing_ok=True)
    if result.returncode != 0:
        return f"{source.name}: KiCad could not parse the {kind} migration probe; see {evidence}"
    if original_hash != probe_hash:
        return (
            f"{source.name}: requires a KiCad {kind} format migration; open/save it with the "
            f"declared toolchain, then rerun the gate (see {evidence})"
        )
    return None


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
    parser.add_argument(
        "--stage",
        choices=["format", "pcb-format", "schematic", "pcb", "all"],
        default="all",
        help="format stages check native format only; run after the first symbol or board",
    )
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
        configured_major = required_major(root)
        cli = find_cli(args.kicad_cli, configured_major)
        projects = source_files(root, ".kicad_pro")
        if not projects:
            raise RuntimeError("no .kicad_pro project found")

        for project_file in projects:
            stem = project_file.with_suffix("")
            label = project_file.stem
            schematic = stem.with_suffix(".kicad_sch")
            board = stem.with_suffix(".kicad_pcb")

            if args.stage in {"format", "schematic", "all"}:
                if not schematic.is_file():
                    failures.append(f"{label}: matching .kicad_sch is missing")
                else:
                    generator_major = schematic_generator_major(schematic)
                    if generator_major is None:
                        failures.append(f"{label}: schematic has no generator_version; cannot verify toolchain")
                    elif generator_major != configured_major:
                        failures.append(
                            f"{label}: schematic generator major {generator_major} does not match "
                            f"required major {configured_major}"
                        )
                    migration_failure = migration_probe(cli, "sch", schematic, output)
                    if migration_failure:
                        failures.append(f"{label}: {migration_failure}")
                    if args.stage in {"schematic", "all"}:
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

            if args.stage in {"pcb-format", "pcb", "all"}:
                if not board.is_file():
                    failures.append(f"{label}: matching .kicad_pcb is missing")
                else:
                    migration_failure = migration_probe(cli, "pcb", board, output)
                    if migration_failure:
                        failures.append(f"{label}: {migration_failure}")
                    if args.stage in {"pcb", "all"}:
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
