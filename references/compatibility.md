# Multi-agent compatibility

Keep `SKILL.md`, `scripts/`, `references/`, and `assets/` platform-neutral. Treat
this repository as the canonical source and keep product-specific metadata in
thin adapters only.

## Supported installations

| Agent | Personal skill location | Adapter |
| --- | --- | --- |
| OpenAI Codex | `~/.codex/skills/pcb-design-system` | `agents/openai.yaml` |
| Claude Code | `~/.claude/skills/pcb-design-system` | none required |
| Gemini CLI | `~/.gemini/skills/pcb-design-system` | none required |
| Antigravity | `~/.gemini/config/skills/pcb-design-system` | none required |

All agents consume the same Agent Skills structure based on `SKILL.md`. Gemini can
also discover `.agents/skills/pcb-design-system` in a workspace.

Run `python scripts/install_skill.py --platform all` once from the canonical checkout
to install or link personal copies. Prefer link mode when the operating system
allows it; auto mode falls back to a copy. Re-run the installer after an update
when copies are used.

## Project-level fallback

Each initialized project contains:

- `AGENTS.md`: authoritative agent-neutral project instructions;
- `CLAUDE.md`: minimal Claude Code pointer to `AGENTS.md`;
- `GEMINI.md`: minimal Gemini pointer to `AGENTS.md`;
- `tools/pcb_design/`: deterministic record and validation tools.

These files make the project understandable without chat history and usable even
when the central skill is unavailable. Project records always take precedence
over an agent's memory or a stale installed skill.

## Portability rules

- Resolve bundled paths from the directory containing `SKILL.md`.
- Do not use model-specific tool names in the core workflow.
- Do not add model-specific frontmatter to `SKILL.md`.
- Keep secrets and personal paths out of the skill and project templates.
- Test both the canonical checkout and an installed copy before release.
- Increment `VERSION` whenever an installed adapter changes; never patch an
  installed copy without promoting the change to the canonical repository.
