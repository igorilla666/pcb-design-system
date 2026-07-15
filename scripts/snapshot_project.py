#!/usr/bin/env python3
"""Create a durable Git and KiCad-source snapshot for a PCB project."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path


SOURCE_SUFFIXES = {".kicad_sch", ".kicad_pcb", ".kicad_pro", ".kicad_sym", ".kicad_mod"}
SKIP_PARTS = {".git", "manufacturing", "docs", "build"}


def git_output(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, check=False, capture_output=True, text=True
    )
    return (result.stdout or result.stderr).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_label(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-") or "snapshot"


def default_evidence_files(root: Path, evidence_dir: Path) -> list[Path]:
    """Return only deterministic gate artifacts, never ad-hoc debug outputs."""
    names = {"electrical-manifest.json", "schematic-review.md", "pcb-review.md"}
    projects = [
        path for path in root.rglob("*.kicad_pro")
        if not any(part in SKIP_PARTS for part in path.relative_to(root).parts)
    ]
    for project in projects:
        label = project.stem
        names.update({
            f"{label}-erc.rpt",
            f"{label}-netlist.xml",
            f"{label}-drc.rpt",
            f"{label}-sch-migration.txt",
            f"{label}-pcb-migration.txt",
        })
    return [evidence_dir / name for name in sorted(names) if (evidence_dir / name).is_file()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--label", default="snapshot")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow a source snapshot from a dirty worktree (not for release evidence)",
    )
    parser.add_argument(
        "--evidence",
        action="append",
        default=[],
        type=Path,
        help="File or directory to copy into the immutable snapshot",
    )
    args = parser.parse_args()

    root = args.project.expanduser().resolve()
    if not (root / "docs").is_dir():
        parser.error(f"not a tracked PCB project: {root}")

    status = git_output(root, "status", "--short")
    if status and not args.allow_dirty:
        parser.error(
            "worktree is dirty; commit or stash source changes before snapshot, "
            "or use --allow-dirty for an explicitly non-release snapshot"
        )

    stamp = dt.datetime.now().astimezone().strftime("%Y%m%d-%H%M")
    output = root / "docs" / "validation" / f"{stamp}-{safe_label(args.label)}"
    output.mkdir(parents=True, exist_ok=False)

    files = sorted(
        path for path in root.rglob("*")
        if path.is_file()
        and (path.suffix in SOURCE_SUFFIXES or ".pretty" in path.parts)
        and ".git" not in path.parts
        and "manufacturing" not in path.parts
    )
    hashes = [f"{sha256(path)}  {path.relative_to(root).as_posix()}" for path in files]
    (output / "sha256sums.txt").write_text("\n".join(hashes) + ("\n" if hashes else ""), encoding="utf-8")

    head = git_output(root, "rev-parse", "HEAD")
    evidence_sources = list(args.evidence)
    default_evidence = root / "build" / "pcb-design-check"
    if not evidence_sources and default_evidence.exists():
        evidence_sources.extend(default_evidence_files(root, default_evidence))
    copied_evidence = 0
    for source in evidence_sources:
        source = source if source.is_absolute() else root / source
        if not source.exists():
            parser.error(f"evidence does not exist: {source}")
        destination = output / "evidence" / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True)
            copied_evidence += sum(1 for path in source.rglob("*") if path.is_file())
        else:
            shutil.copy2(source, destination)
            copied_evidence += 1
    report = [
        "# Project snapshot",
        "",
        f"- Timestamp: {dt.datetime.now().astimezone().isoformat(timespec='minutes')}",
        f"- Label: {args.label}",
        f"- Git HEAD: {head or 'not available'}",
        f"- KiCad source files hashed: {len(files)}",
        f"- Evidence files copied: {copied_evidence}",
        "",
        "## Git status",
        "",
        "```text",
        status or "clean",
        "```",
        "",
        "A release snapshot must contain the applicable ERC, DRC, manufacturing,",
        "and measurement evidence; zero copied files is not release evidence.",
    ]
    (output / "snapshot.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Created snapshot: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
