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
PROJECT_TOOL_NAMES = (
    "check_project.py",
    "check_kicad.py",
    "record_event.py",
    "snapshot_project.py",
)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-") or "pcb-project"


def git_config(key: str, *, global_only: bool = False) -> str:
    command = ["git", "config"]
    if global_only:
        command.append("--global")
    command.extend(["--get", key])
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def run_git(target: Path, git_name: str, git_email: str) -> None:
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=target,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", git_name],
        cwd=target,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", git_email],
        cwd=target,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "."], cwd=target, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initialize PCB project records"],
        cwd=target,
        check=True,
        capture_output=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="Human-readable project name")
    parser.add_argument("target", type=Path, help="New or empty target directory")
    parser.add_argument("--slug", help="Repository/project slug")
    parser.add_argument("--repository-url", default="local only")
    parser.add_argument("--no-git", action="store_true", help="Do not initialize Git")
    parser.add_argument("--git-name", help="Local Git author name for the new repository")
    parser.add_argument("--git-email", help="Local Git author email for the new repository")
    args = parser.parse_args()

    git_name = args.git_name or git_config("user.name", global_only=True)
    git_email = args.git_email or git_config("user.email", global_only=True)
    if not args.no_git and (not git_name or not git_email):
        parser.error(
            "Git identity is missing. Pass --git-name and --git-email or configure "
            "git config --global user.name/user.email. Values are never invented."
        )

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
        "{{REPOSITORY_URL}}": args.repository_url,
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

    project_tools = target / "tools" / "pcb_design"
    project_tools.mkdir(parents=True, exist_ok=True)
    for name in PROJECT_TOOL_NAMES:
        shutil.copy2(SKILL_ROOT / "scripts" / name, project_tools / name)
    shutil.copy2(SKILL_ROOT / "VERSION", project_tools / "SYSTEM_VERSION")

    if not args.no_git:
        try:
            run_git(target, git_name, git_email)
        except (OSError, subprocess.CalledProcessError) as exc:
            print(f"Git initialization failed: {exc}", file=sys.stderr)
            return 1
    print(f"Created PCB project: {target}")
    print(f"Process version: {replacements['{{SYSTEM_VERSION}}']}")
    if not args.no_git:
        print("Git repository initialized on main with an initial commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
