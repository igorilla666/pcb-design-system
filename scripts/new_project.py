#!/usr/bin/env python3
"""Create one PCB project, one local Git repository, and one GitHub repository."""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from init_project import slugify


SCRIPT_ROOT = Path(__file__).resolve().parent
INIT_SCRIPT = SCRIPT_ROOT / "init_project.py"
API_ROOT = "https://api.github.com"


@dataclass
class GitHubAuth:
    mode: str
    login: str
    token: str | None = None


def run(
    command: list[str],
    *,
    cwd: Path | None = None,
    input_text: str | None = None,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        input=input_text,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )


def git_global(key: str) -> str:
    result = run(["git", "config", "--global", "--get", key])
    return result.stdout.strip() if result.returncode == 0 else ""


def prompt(label: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or (default or "")


def require_value(value: str | None, label: str, default: str | None = None) -> str:
    if value:
        return value
    if sys.stdin.isatty():
        answer = prompt(label, default)
        if answer:
            return answer
    raise RuntimeError(f"missing {label.lower()}")


def api_request(token: str, method: str, path: str, payload: dict[str, object] | None = None) -> tuple[int, dict[str, object]]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        API_ROOT + path,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "pcb-design-system",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed = {"message": body}
        return exc.code, parsed


def credential_manager_token() -> str:
    if not shutil.which("git"):
        return ""
    result = run(
        ["git", "credential", "fill"],
        input_text="protocol=https\nhost=github.com\n\n",
    )
    if result.returncode != 0:
        return ""
    values = {}
    for line in result.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values.get("password", "")


def github_auth() -> GitHubAuth:
    gh = shutil.which("gh")
    if gh:
        status = run([gh, "auth", "status"])
        if status.returncode == 0:
            user = run([gh, "api", "user", "--jq", ".login"])
            if user.returncode == 0 and user.stdout.strip():
                return GitHubAuth("gh", user.stdout.strip())

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or credential_manager_token()
    if token:
        status, user = api_request(token, "GET", "/user")
        login = str(user.get("login", ""))
        if status == 200 and login:
            return GitHubAuth("api", login, token)

    raise RuntimeError(
        "GitHub authentication is unavailable. One-time setup: install GitHub CLI "
        "and run 'gh auth login', set GH_TOKEN, or run "
        "'git credential-manager github login'."
    )


def ensure_remote_available(auth: GitHubAuth, owner: str, repository: str) -> None:
    full_name = f"{owner}/{repository}"
    if auth.mode == "gh":
        result = run(["gh", "repo", "view", full_name, "--json", "name"])
        if result.returncode == 0:
            raise RuntimeError(f"GitHub repository already exists: {full_name}")
        return
    status, _ = api_request(auth.token or "", "GET", f"/repos/{full_name}")
    if status == 200:
        raise RuntimeError(f"GitHub repository already exists: {full_name}")
    if status != 404:
        raise RuntimeError(f"cannot verify GitHub repository availability: HTTP {status}")


def create_remote(auth: GitHubAuth, owner: str, repository: str, description: str, public: bool, target: Path) -> str:
    full_name = f"{owner}/{repository}"
    if auth.mode == "gh":
        command = [
            "gh", "repo", "create", full_name,
            "--source", str(target), "--remote", "origin", "--push",
            "--public" if public else "--private",
        ]
        if description:
            command.extend(["--description", description])
        result = run(command, cwd=target)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    else:
        payload: dict[str, object] = {
            "name": repository,
            "private": not public,
            "description": description,
            "auto_init": False,
        }
        endpoint = "/user/repos" if owner.casefold() == auth.login.casefold() else f"/orgs/{owner}/repos"
        status, response = api_request(auth.token or "", "POST", endpoint, payload)
        if status != 201:
            raise RuntimeError(f"GitHub repository creation failed: HTTP {status} {response.get('message', '')}")
        remote = f"https://github.com/{full_name}.git"
        result = run(["git", "remote", "add", "origin", remote], cwd=target)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
        encoded = base64.b64encode(f"x-access-token:{auth.token}".encode()).decode()
        environment = os.environ.copy()
        environment.update(
            {
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "http.extraHeader",
                "GIT_CONFIG_VALUE_0": f"Authorization: Basic {encoded}",
            }
        )
        result = run(
            ["git", "push", "-u", "origin", "main"],
            cwd=target,
            environment=environment,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return f"https://github.com/{full_name}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", nargs="?", help="Human-readable project name")
    parser.add_argument("--target", type=Path, help="Exact directory for the new repository")
    parser.add_argument("--repo", help="GitHub repository name; defaults to project slug")
    parser.add_argument("--owner", help="GitHub account or organization; defaults to authenticated user")
    parser.add_argument("--description", default="PCB project managed with pcb-design-system")
    visibility = parser.add_mutually_exclusive_group()
    visibility.add_argument("--public", action="store_true")
    visibility.add_argument("--private", action="store_true")
    parser.add_argument("--git-name")
    parser.add_argument("--git-email")
    parser.add_argument("--no-github", action="store_true", help="Create only the local Git repository")
    parser.add_argument("--dry-run", action="store_true", help="Show the plan without creating anything")
    args = parser.parse_args()

    try:
        name = require_value(args.name, "Project name")
        repository = args.repo or slugify(name)
        default_target = str((Path.cwd() / repository).resolve())
        target_text = str(args.target) if args.target else require_value(None, "Repository folder", default_target)
        target = Path(target_text).expanduser().resolve()
        if target.exists() and any(target.iterdir()):
            raise RuntimeError(f"target is not empty: {target}")

        git_name = args.git_name or git_global("user.name")
        git_email = args.git_email or git_global("user.email")
        git_name = require_value(git_name, "Git author name")
        git_email = require_value(git_email, "Git author email")

        public = args.public

        if args.dry_run:
            print(f"Project: {name}")
            print(f"Local repository: {target}")
            print(f"GitHub repository: {'disabled' if args.no_github else repository}")
            print(f"Visibility: {'public' if public else 'private'}")
            print("Dry run: no files or remote repositories created.")
            return 0

        auth = None if args.no_github else github_auth()
        owner = args.owner or (auth.login if auth else "")
        if auth:
            ensure_remote_available(auth, owner, repository)

        command = [
            sys.executable,
            str(INIT_SCRIPT),
            name,
            str(target),
            "--slug",
            repository,
            "--repository-url",
            f"https://github.com/{owner}/{repository}" if auth else "local only",
            "--git-name",
            git_name,
            "--git-email",
            git_email,
        ]
        result = run(command)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
        print(result.stdout.strip())

        if auth:
            url = create_remote(auth, owner, repository, args.description, public, target)
            print(f"GitHub repository created and pushed: {url}")
        else:
            print("GitHub creation skipped by --no-github.")
        return 0
    except (OSError, RuntimeError) as exc:
        print(f"New project failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
