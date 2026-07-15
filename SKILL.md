---
name: pcb-design-system
description: Initialize, track, audit, and release PCB projects with a persistent Git-backed record, especially KiCad projects. Use when an AI coding agent starts or resumes a PCB design, changes schematics or layouts, selects components, records design decisions, runs ERC/DRC, prepares BOM/CPL/Gerbers, validates prototypes, creates hardware revisions, or promotes lessons into a reusable design process.
---

# PCB Design System

Make project files and Git the source of truth. Never rely on chat history as the
only record of a decision, test, risk, or release state.

Resolve `SKILL_ROOT` as the absolute directory containing this `SKILL.md`. Resolve
all bundled `scripts/`, `references/`, and `assets/` paths from `SKILL_ROOT`, not
from the current working directory. This keeps the workflow portable across AI
agents and installation locations.

## Start or resume

For a new project, run:

`python "<SKILL_ROOT>/scripts/init_project.py" "Project name" "absolute/target/path"`

For an existing project:

1. Locate the repository root.
2. Read `AGENTS.md` when present.
3. Read `docs/PROJECT_STATE.md`.
4. Read the latest entries in `docs/PROJECT_LOG.md`.
5. Read applicable files in `docs/decisions/`.
6. Check `git status` and preserve unrelated user changes.
7. State the current phase, open risks, and intended change before editing.

If the expected records are missing, create them from
`<SKILL_ROOT>/assets/project-template/` without overwriting hardware files.

Prefer the project-local tools in `tools/pcb_design/`. For an older project that
does not contain them, run the matching script from `<SKILL_ROOT>/scripts/`.

## Work protocol

Before a meaningful change:

1. Confirm requirements and the safe state of affected outputs.
2. Identify the authoritative schematic, PCB, variant, and manufacturing package.
3. Create a Git commit or named snapshot.
4. Close KiCad before raw or automated edits to KiCad files.
5. Read [`references/kicad-safety.md`](references/kicad-safety.md) when touching
   `.kicad_*` files.

During the change:

- Treat symbol pin, datasheet function, and footprint pad as one contract.
- Modify the schematic first, then update the PCB from that schematic.
- Keep baseline and production variants physically independent.
- Record sources, MPNs, limits, assumptions, and vendor confirmations.
- Do not treat zero ERC/DRC errors as functional proof.

After the change:

1. Export/check the netlist when connectivity changed.
2. Run ERC, update PCB, refill zones, and run DRC as applicable.
3. Review polarities, current paths, boot states, connector pinouts, and
   worst-case electrical limits manually.
4. Run `python tools/pcb_design/snapshot_project.py . --label LABEL`.
5. Run `python tools/pcb_design/record_event.py .` with the applicable fields.
6. Update `docs/PROJECT_STATE.md`, open risks, and next actions.
7. Commit one coherent change.

Use [`references/workflow.md`](references/workflow.md) for design and release
gates. Use [`references/records.md`](references/records.md) for log, state, ADR,
and evidence formats. Use
[`references/lessons-water-controller.md`](references/lessons-water-controller.md)
when reviewing power, grounding, relays, WS2812, RS-485, symbols, or manufacturing
variants. Use [`references/compatibility.md`](references/compatibility.md) when
installing or maintaining the skill across different AI agents.

## Decisions and evidence

Create an ADR in `docs/decisions/` when a choice:

- changes architecture, grounding, power, module, pin map, or connector;
- is expensive to reverse after PCB fabrication;
- accepts a warning, derating, substitution, or vendor ambiguity;
- creates a new production variant.

Record context, options, decision, reasons, consequences, sources, and validation.
Do not rewrite history: supersede an ADR with a newer ADR.

## Release rule

Do not call a design production-ready until:

- ERC has zero unexplained errors;
- DRC has zero errors and zero unconnected pads;
- warnings and exclusions are documented;
- component/footprint/pinout audit is complete;
- power and thermal budgets include simultaneous worst-case loads;
- BOM, CPL, Gerbers, drill files, and checksums come from the same revision;
- assembly preview and polarized-component orientations are checked;
- first-article tests and remaining risks are recorded.

Run `python tools/pcb_design/check_project.py . --strict` before handoff or
release. Use the matching bundled script when project-local tools are absent.

## Improve the system

At project milestones, review `docs/LESSONS.md`. Promote a lesson into this skill
or its references when it is reusable across projects, especially after a repeat
failure or a successful preventive check. Increment `VERSION` for material process
changes and keep old projects tied to the version recorded at initialization.
