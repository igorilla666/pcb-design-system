# PCB Design System

A reusable, Git-backed workflow for designing, reviewing, and releasing KiCad
PCB projects with AI coding agents. It keeps requirements, decisions, project
state, validation evidence, and manufacturing releases in the repository instead
of relying on chat history.

## Highlights

- Compatible with OpenAI Codex, Claude Code, and Gemini CLI.
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

To initialize a project directly:

```bash
python scripts/init_project.py "Project name" "/absolute/project/path"
```

See [`SKILL.md`](SKILL.md) for the workflow and
[`references/compatibility.md`](references/compatibility.md) for platform paths.

## License

Licensed under the [Apache License 2.0](LICENSE).
