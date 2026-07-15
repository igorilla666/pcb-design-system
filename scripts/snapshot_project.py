#!/usr/bin/env python3
"""Create a durable Git and KiCad-source snapshot for a PCB project."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
import subprocess
import sys
from pathlib import Path


SOURCE_SUFFIXES = {".kicad_sch", ".kicad_pcb", ".kicad_pro", ".kicad_sym", ".kicad_mod"}


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--label", default="snapshot")
    args = parser.parse_args()

    root = args.project.expanduser().resolve()
    if not (root / "docs").is_dir():
        parser.error(f"not a tracked PCB project: {root}")

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
    status = git_output(root, "status", "--short")
    report = [
        "# Project snapshot",
        "",
        f"- Timestamp: {dt.datetime.now().astimezone().isoformat(timespec='minutes')}",
        f"- Label: {args.label}",
        f"- Git HEAD: {head or 'not available'}",
        f"- KiCad source files hashed: {len(files)}",
        "",
        "## Git status",
        "",
        "```text",
        status or "clean",
        "```",
        "",
        "ERC, DRC, measurements, and manufacturing validation reports should be",
        "copied into this directory before a release decision.",
    ]
    (output / "snapshot.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Created snapshot: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
