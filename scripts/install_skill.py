#!/usr/bin/env python3
"""Install the canonical PCB Design System skill for supported AI agents."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import sys
from pathlib import Path


SKILL_NAME = "pcb-design-system"
SKILL_ROOT = Path(__file__).resolve().parents[1]
IGNORE_NAMES = {".git", "__pycache__", "test-output"}


def platform_roots(home: Path, use_environment: bool = True) -> dict[str, Path]:
    codex_home = (
        Path(os.environ.get("CODEX_HOME", home / ".codex"))
        if use_environment
        else home / ".codex"
    )
    return {
        "codex": codex_home / "skills",
        "claude": home / ".claude" / "skills",
        "gemini": home / ".gemini" / "skills",
    }


def ignored(_directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name in IGNORE_NAMES or name.endswith(".pyc")
    }


def same_path(left: Path, right: Path) -> bool:
    try:
        return left.resolve() == right.resolve()
    except OSError:
        return False


def validate_install(destination: Path) -> None:
    required = [
        destination / "SKILL.md",
        destination / "VERSION",
        destination / "scripts" / "init_project.py",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError("incomplete skill installation: " + ", ".join(missing))


def install_one(
    platform: str,
    destination: Path,
    mode: str,
    force: bool,
    dry_run: bool,
) -> str:
    source = SKILL_ROOT.resolve()
    if same_path(source, destination):
        return f"{platform}: canonical checkout is already active at {destination}"
    if destination.is_symlink() and same_path(source, destination):
        return f"{platform}: already linked to {source}"

    backup: Path | None = None
    if destination.exists() or destination.is_symlink():
        if not force:
            raise FileExistsError(
                f"{platform} destination exists: {destination}; use --force to replace it"
            )
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = destination.with_name(f"{destination.name}.backup-{stamp}")
        if backup.exists() or backup.is_symlink():
            raise FileExistsError(f"backup destination already exists: {backup}")

    if dry_run:
        action = "link or copy" if mode == "auto" else mode
        return f"{platform}: would {action} {source} to {destination}"

    destination.parent.mkdir(parents=True, exist_ok=True)
    if backup:
        destination.rename(backup)

    installed_mode = mode
    try:
        if mode in {"auto", "link"}:
            try:
                destination.symlink_to(source, target_is_directory=True)
                installed_mode = "link"
            except OSError:
                if mode == "link":
                    raise
                shutil.copytree(source, destination, ignore=ignored)
                installed_mode = "copy"
        else:
            shutil.copytree(source, destination, ignore=ignored)
            installed_mode = "copy"
        validate_install(destination)
    except Exception:
        if destination.is_symlink():
            destination.unlink()
        elif destination.exists():
            shutil.rmtree(destination)
        if backup:
            backup.rename(destination)
        raise

    backup_note = f"; previous install saved as {backup}" if backup else ""
    return f"{platform}: installed by {installed_mode} at {destination}{backup_note}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--platform",
        choices=["codex", "claude", "gemini", "all"],
        default="all",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "link", "copy"],
        default="auto",
        help="auto tries a link first and falls back to a copy",
    )
    parser.add_argument(
        "--home",
        type=Path,
        help="Override the user home directory; useful for testing",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    home = (args.home or Path.home()).expanduser().resolve()
    roots = platform_roots(home, use_environment=args.home is None)
    platforms = list(roots) if args.platform == "all" else [args.platform]

    failures: list[str] = []
    for platform in platforms:
        destination = roots[platform] / SKILL_NAME
        try:
            print(
                install_one(
                    platform,
                    destination,
                    args.mode,
                    args.force,
                    args.dry_run,
                )
            )
        except (OSError, RuntimeError) as exc:
            failures.append(f"{platform}: {exc}")

    if failures:
        print("Installation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
