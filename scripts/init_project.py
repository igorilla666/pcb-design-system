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


def checked_git(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            command,
            output=result.stdout,
            stderr=result.stderr,
        )
    return result


def ensure_git_directory_is_safe(target: Path) -> bool:
    probe = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        cwd=target,
        check=False,
        capture_output=True,
        text=True,
    )
    if probe.returncode == 0:
        return False

    details = f"{probe.stdout}\n{probe.stderr}".casefold()
    if "detected dubious ownership" not in details or "safe.directory" not in details:
        raise subprocess.CalledProcessError(
            probe.returncode,
            probe.args,
            output=probe.stdout,
            stderr=probe.stderr,
        )

    checked_git(
        ["git", "config", "--global", "--add", "safe.directory", str(target)]
    )
    checked_git(["git", "rev-parse", "--git-dir"], cwd=target)
    return True


def remove_safe_directory(target: Path) -> None:
    subprocess.run(
        [
            "git",
            "config",
            "--global",
            "--unset-all",
            "--fixed-value",
            "safe.directory",
            str(target),
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def run_git(target: Path, git_name: str, git_email: str) -> bool:
    checked_git(
        ["git", "init", "-b", "main"],
        cwd=target,
    )
    safe_directory_added = ensure_git_directory_is_safe(target)
    try:
        checked_git(["git", "config", "user.name", git_name], cwd=target)
        checked_git(["git", "config", "user.email", git_email], cwd=target)
        checked_git(["git", "add", "."], cwd=target)
        checked_git(
            ["git", "commit", "-m", "Initialize PCB project records"],
            cwd=target,
        )
    except (OSError, subprocess.CalledProcessError):
        if safe_directory_added:
            remove_safe_directory(target)
        raise
    return safe_directory_added


def describe_git_error(error: OSError | subprocess.CalledProcessError) -> str:
    if not isinstance(error, subprocess.CalledProcessError):
        return str(error)
    details = "\n".join(
        value.strip()
        for value in (error.stderr or "", error.output or "")
        if value and value.strip()
    )
    return f"{error}{': ' + details if details else ''}"


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
            safe_directory_added = run_git(target, git_name, git_email)
        except (OSError, subprocess.CalledProcessError) as exc:
            print(f"Git initialization failed: {describe_git_error(exc)}", file=sys.stderr)
            return 1
    print(f"Created PCB project: {target}")
    print(f"Process version: {replacements['{{SYSTEM_VERSION}}']}")
    if not args.no_git:
        print("Git repository initialized on main with an initial commit.")
        if safe_directory_added:
            print(f"Git safe.directory added for this network repository only: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
