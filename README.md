# PCB Design System

A reusable, Git-backed workflow for designing, reviewing, and releasing KiCad
PCB projects with AI coding agents. It keeps requirements, decisions, project
state, validation evidence, and manufacturing releases in the repository instead
of relying on chat history.

## Highlights

- Compatible with OpenAI Codex, Claude Code, Gemini CLI, and Antigravity.
- Provides a ready-to-use PCB project structure and release checklist.
- Records decisions, risks, component choices, ERC/DRC results, and snapshots.
- Includes lessons learned from a real water-controller PCB project.

## Install

Requires Python 3 and Git.

```bash
git clone https://github.com/igorilla666/pcb-design-system.git
cd pcb-design-system
python scripts/install_skill.py --platform all
```

Then ask your agent to use `pcb-design-system` when starting or resuming a PCB
project.

For a new local and GitHub repository, run:

```bash
python scripts/new_project.py
```

The launcher asks for the exact destination folder and defaults to a private
GitHub repository. Authenticate once with `gh auth login`, `GH_TOKEN`, or
`git credential-manager github login`. Use `--dry-run` to preview or
`--no-github` only for an intentionally offline project.

See [`SKILL.md`](SKILL.md) for the workflow and
[`references/compatibility.md`](references/compatibility.md) for platform paths.

## License

Licensed under the [Apache License 2.0](LICENSE).
