#!/usr/bin/env python3
"""Initialize a PCB project from the bundled template."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "project-template"


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-") or "pcb-project"


def git_config(target: Path, key: str) -> str:
    result = subprocess.run(
        ["git", "config", "--get", key],
        cwd=target,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def run_git(target: Path, git_name: str | None, git_email: str | None) -> list[str]:
    messages: list[str] = []
    try:
        subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)
        if git_name:
            subprocess.run(
                ["git", "config", "user.name", git_name],
                cwd=target,
                check=True,
                capture_output=True,
            )
        if git_email:
            subprocess.run(
                ["git", "config", "user.email", git_email],
                cwd=target,
                check=True,
                capture_output=True,
            )
        if not git_config(target, "user.name") or not git_config(target, "user.email"):
            messages.append(
                "Git repository initialized without a commit because user.name "
                "or user.email is not configured. Pass --git-name and --git-email."
            )
            return messages
        subprocess.run(["git", "add", "."], cwd=target, check=True, capture_output=True)
        result = subprocess.run(
            ["git", "commit", "-m", "Initialize PCB project records"],
            cwd=target,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            messages.append(
                "Git initialized, but the initial commit was not created: "
                + (result.stderr.strip() or result.stdout.strip())
            )
        else:
            messages.append("Git repository initialized with an initial commit.")
    except (OSError, subprocess.CalledProcessError) as exc:
        messages.append(f"Git initialization skipped or incomplete: {exc}")
    return messages


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="Human-readable project name")
    parser.add_argument("target", type=Path, help="New or empty target directory")
    parser.add_argument("--slug", help="Repository/project slug")
    parser.add_argument("--no-git", action="store_true", help="Do not initialize Git")
    parser.add_argument("--git-name", help="Local Git author name for the new repository")
    parser.add_argument("--git-email", help="Local Git author email for the new repository")
    args = parser.parse_args()

    target = args.target.expanduser().resolve()
    if target.exists() and any(target.iterdir()):
        parser.error(f"target is not empty: {target}")
    target.mkdir(parents=True, exist_ok=True)

    if not TEMPLATE_ROOT.is_dir():
        parser.error(f"template not found: {TEMPLATE_ROOT}")

    shutil.copytree(TEMPLATE_ROOT, target, dirs_exist_ok=True)
    replacements = {
        "{{PROJECT_NAME}}": args.name,
        "{{PROJECT_SLUG}}": args.slug or slugify(args.name),
        "{{DATE}}": dt.date.today().isoformat(),
        "{{SYSTEM_VERSION}}": (SKILL_ROOT / "VERSION").read_text(encoding="utf-8").strip(),
    }

    for path in target.rglob("*"):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for old, new in replacements.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8", newline="\n")

    messages = [] if args.no_git else run_git(target, args.git_name, args.git_email)
    print(f"Created PCB project: {target}")
    print(f"Process version: {replacements['{{SYSTEM_VERSION}}']}")
    for message in messages:
        print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
