---
name: pcb-design-system
description: Initialize, track, audit, and release PCB projects with a persistent Git-backed record, especially KiCad projects. Use when Codex starts or resumes a PCB design, changes schematics or layouts, selects components, records design decisions, runs ERC/DRC, prepares BOM/CPL/Gerbers, validates prototypes, creates hardware revisions, or promotes lessons into a reusable design process.
---

# PCB Design System

Make project files and Git the source of truth. Never rely on chat history as the
only record of a decision, test, risk, or release state.

## Start or resume

For a new project, run:

`python scripts/init_project.py "Project name" "absolute/target/path"`

For an existing project:

1. Locate the repository root.
2. Read `docs/PROJECT_STATE.md`.
3. Read the latest entries in `docs/PROJECT_LOG.md`.
4. Read applicable files in `docs/decisions/`.
5. Check `git status` and preserve unrelated user changes.
6. State the current phase, open risks, and intended change before editing.

If the expected records are missing, create them from
`assets/project-template/` without overwriting hardware files.

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
4. Run `scripts/snapshot_project.py` for a durable validation snapshot.
5. Append the event with `scripts/record_event.py`.
6. Update `docs/PROJECT_STATE.md`, open risks, and next actions.
7. Commit one coherent change.

Use [`references/workflow.md`](references/workflow.md) for design and release
gates. Use [`references/records.md`](references/records.md) for log, state, ADR,
and evidence formats. Use
[`references/lessons-water-controller.md`](references/lessons-water-controller.md)
when reviewing power, grounding, relays, WS2812, RS-485, symbols, or manufacturing
variants.

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

Run `scripts/check_project.py PROJECT_ROOT` before handoff or release.

## Improve the system

At project milestones, review `docs/LESSONS.md`. Promote a lesson into this skill
or its references when it is reusable across projects, especially after a repeat
failure or a successful preventive check. Increment `VERSION` for material process
changes and keep old projects tied to the version recorded at initialization.
