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

## Create or resume

On Windows, prefer the graphical launcher:

`launcher/PCBProjectLauncher.exe`

It asks for the project, exact destination, Git identity, GitHub visibility, and
whether to continue in ChatGPT/Codex or Gemini/Antigravity. The selected agent
only controls which application opens; the repository and records remain
agent-neutral.

For a terminal or non-Windows environment, run the interactive launcher:

`python "<SKILL_ROOT>/scripts/new_project.py"`

It asks for the project name, exact destination folder, Git identity, and GitHub
visibility. It creates an independent local repository, initial commit, GitHub
repository, `origin`, and first push. For automation, pass `name`, `--target`,
`--git-name`, and `--git-email`; GitHub remains enabled unless `--no-github` is
explicitly requested. Never invent Git identity or repository ownership.

Use `init_project.py` only for local/offline initialization.

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

Prefer project-local tools in `tools/pcb_design/`; they preserve the process
version used to create that repository.

## Work protocol

Before a meaningful change:

1. Confirm requirements and the safe state of affected outputs.
2. Identify the authoritative schematic, PCB, variant, and manufacturing package.
   Read `docs/kicad-toolchain.json`; the declared KiCad major is a hard project
   requirement, not a best-effort preference.
3. Create a Git commit or named snapshot.
4. Close KiCad before raw or automated edits to KiCad files.
5. Read [`references/kicad-safety.md`](references/kicad-safety.md) when touching
   `.kicad_*` files.
6. Read `docs/DEPENDENCIES.md`. The repository, declared KiCad toolchain, and
   its approved ledger are the only allowed sources. Do not scan other local
   folders or repositories for examples, code, symbols, or syntax.
7. Read `docs/tooling-manifest.json`. Only its approved scripts may affect
   authoritative hardware. Historical or diagnostic scripts are quarantined
   until reviewed, tested, and promoted under `tools/pcb_design/`.

For a new schematic or generator, place or generate one representative symbol,
then immediately run `python tools/pcb_design/check_kicad.py . --stage format`.
It validates the declared toolchain and proves that KiCad would not migrate that
file. Do not add further symbols, wiring, or generated circuitry until it passes.

When creating a PCB, create or generate only a minimal board first, then run
`python tools/pcb_design/check_kicad.py . --stage pcb-format`. It validates the
board syntax and migration state without requiring a completed layout. Do not
place, route, or generate further PCB content until it passes. Once it passes,
use KiCad's Update PCB from Schematic operation before any automated or manual
placement. The resulting board, not a script-created footprint list, is the
only allowed starting point for placement.

During the change:

- Treat symbol pin, datasheet function, and footprint pad as one contract.
- Modify the schematic first, then update the PCB from that schematic.
- Never create, load, or match PCB footprints independently of the approved
  schematic. An LLM or generator may position only the references and nets
  imported by KiCad from that schematic; a missing footprint assignment blocks
  the flow.
- Keep baseline and production variants physically independent.
- Record sources, MPNs, limits, assumptions, and vendor confirmations.
- Do not treat zero ERC/DRC errors as functional proof.
- Never generate, accept, or release a KiCad file with an undeclared or
  mismatched toolchain version. The applicable KiCad CLI must parse it and its
  non-forced upgrade command must leave a disposable copy unchanged.
- Resolve `kicad-cli` only for the exact major in `docs/kicad-toolchain.json`.
  Never try KiCad 8 or another installed major as a fallback. If the declared
  toolchain is unavailable, stop and ask the user to install/select it.
- Before authoritative generation or a batch review, run
  `python tools/pcb_design/check_tool_policy.py .`. Do not execute unregistered
  historical or diagnostic scripts; preserve candidates in `legacy/`, review
  them in isolation, add deterministic tests, then promote a reviewed copy.
- Keep any KiCad generator or transformer used to create authoritative files in
  the repository; hidden scratch scripts are not reproducible evidence.
- Keep exploratory generators only in ignored `scratch/`. Before accepting their
  output, promote the final generator and its declared inputs to
  `tools/pcb_design/generators/`.
- When an external asset or code is genuinely needed, stop before using it. Get
  user approval, record provenance/version/license/hash in `DEPENDENCIES.md`,
  promote the minimum material into a versioned repository path, test it, then
  use it. Never make authoritative output depend on discovered machine-local
  files.

For a readability-only schematic pass, first write
`docs/schematic-layout.json`: sheet size, grid, reading flow, functional-block
rectangles/titles, and component assignment. This is the canonical generator
input, so the first output can already have planned visual zones. Preserve a
validated electrical-manifest baseline before rearranging content. Keep
`docs/schematic-layout.md` as the concise human review record. Use titled block
boundaries and a readable grid, then inspect the authoritative file in the
declared KiCad version. ERC alone does not prove the schematic is readable.

For a generated schematic, keep electrical intent in
`docs/schematic-source.json` and visual geometry in
`docs/schematic-layout.json`; do not bury components, pin maps, or coordinates
in Python literals. For generated or assisted PCB placement, first write
`docs/pcb-layout.json` with outline, cut-outs, footprint sources, placements and
edge-clearance requirements. Its source must be the board updated from the
approved schematic. A generator may create only a draft until the normal format,
parity, DRC and human placement-review gates pass.

After the change:

1. Run `python tools/pcb_design/check_kicad.py . --stage schematic` after
   connectivity changes; it runs ERC and audits the exported netlist.
   Export `python tools/pcb_design/export_electrical_manifest.py .` when a
   compact, deterministic electrical review or Git diff is useful. Compare
   artifacts with `diff_electrical_manifest.py`; neither replaces KiCad ERC.
   Prefer `review_schematic_batch.py` to perform the gate, manifest export, and
   optional baseline diff in one call and produce a single compact report.
   It also checks the accepted visual-layout plan.
2. Update PCB, refill zones, then run the same tool with `--stage pcb`.
3. Review polarities, current paths, boot states, connector pinouts, and
   worst-case electrical limits manually.
4. Run `python tools/pcb_design/record_event.py .` with the applicable fields,
   then update `docs/PROJECT_STATE.md`, open risks, and next actions.
5. Commit the validated source state. Then run `snapshot_project.py`; it rejects
   a dirty worktree unless `--allow-dirty` explicitly marks a non-release
   snapshot. It includes the latest deterministic check evidence from
   `build/pcb-design-check/`.
6. Commit the resulting snapshot evidence.

Use [`references/workflow.md`](references/workflow.md) for design and release
gates. Use [`references/records.md`](references/records.md) for log, state, ADR,
and evidence formats. Use
[`references/lessons-water-controller.md`](references/lessons-water-controller.md)
when reviewing power, grounding, relays, WS2812, RS-485, symbols, or manufacturing
variants. Use [`references/compatibility.md`](references/compatibility.md) when
installing or maintaining the skill across different AI agents.
Use [`references/dependencies.md`](references/dependencies.md) for the portable
dependency boundary and promotion procedure.
Use [`references/tooling.md`](references/tooling.md) for the historical-script
quarantine and exact-KiCad resolution rules.
Use [`references/generator-contract.md`](references/generator-contract.md) for
the declarative schematic and PCB generator inputs.

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

Run both record and KiCad gates before handoff. `check_project.py --strict`
validates only repository records and portability; it is never electrical proof.

## Improve the system

At project milestones, review `docs/LESSONS.md`. Promote a lesson into this skill
or its references when it is reusable across projects, especially after a repeat
failure or a successful preventive check. Increment `VERSION` for material process
changes and keep old projects tied to the version recorded at initialization.
