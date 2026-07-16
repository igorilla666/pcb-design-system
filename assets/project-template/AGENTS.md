# PCB project agent instructions

Use repository files and Git as the source of truth. Do not rely on chat history
for project state, decisions, risks, tests, or release status.

Before changing hardware:

1. Read `docs/PROJECT_STATE.md` and the latest `docs/PROJECT_LOG.md` entries.
2. Read applicable ADRs in `docs/decisions/`.
3. Check `git status` and preserve unrelated changes.
4. Identify the authoritative schematic, PCB, revision, and production variant.
5. Close KiCad before editing `.kicad_*` files outside KiCad.
6. Set `docs/kicad-toolchain.json` to the exact KiCad major version used for
   this project. Do not generate or edit hardware until it is declared.
7. Read `docs/DEPENDENCIES.md` and `docs/tooling-manifest.json`. Use only their allowed sources and approved tools. Do not scan or
   reuse material outside the repository/toolchain boundary without explicit
   user approval and promotion into the repository.

## Dependency boundary

The project repository, declared KiCad toolchain, and dependency ledger are the
only allowed sources. Do not search adjacent repositories, drives, home folders,
cloud folders, or previous projects for examples, syntax, code, symbols, or
templates. If an external resource is required, stop and record source, reason,
version, license, hash, destination, and user approval in `DEPENDENCIES.md`.
Promote and test the minimum required resource before using it in authoritative
hardware. Never set component or footprint defaults from a discovered project.

Apply schematic changes first. Verify symbol pin, datasheet function, and
footprint pad as one contract. Store any generator used for authoritative KiCad
files in this repository; do not rely on agent scratch files.

## Tool boundary

Run only scripts with `status: approved` in `docs/tooling-manifest.json` when
they can affect authoritative hardware. Never run historical, diagnostic, or
unregistered scripts as a shortcut. Retain potentially useful historical tools
under `tools/pcb_design/legacy/` with `status: quarantined`; first review and
test them in an isolated fixture, remove external discovery and version fallback,
then promote the reviewed script and its tests out of `legacy/`.

The KiCad major in `docs/kicad-toolchain.json` is exact. A KiCad 8 executable or
library is not an acceptable fallback for a project declared for KiCad 10 (or
any other major). Stop and tell the user that the declared major is unavailable.

Plan and review readability separately from electrical connectivity. Before a
readability pass, complete `docs/schematic-layout.json` with the sheet, grid,
block bounds, titles, and component assignments. It is the canonical input for
any generator. Keep `docs/schematic-layout.md` as the concise human review
record. Keep experiments in ignored
`scratch/`, but promote any generator that produces an authoritative schematic
to `tools/pcb_design/generators/` with its declared inputs.

Required gates:

- `check_project.py --strict` checks records only; never call it electrical proof.
- `check_dependency_policy.py` must pass before authoritative generation or a
  batch review; it records a reproducible dependency boundary.
- `check_tool_policy.py` must pass before authoritative generation or a batch
  review; it proves every available project script is reviewed and registered.
- `check_kicad.py` requires the installed KiCad CLI major and schematic
  `generator_version` to match `docs/kicad-toolchain.json`. A board must also
  be parseable by that CLI during its DRC gate. It tests disposable copies with
  KiCad's non-forced upgrade command: any required migration blocks the gate.
- Immediately after the first schematic symbol is placed or generated, run
  `python tools/pcb_design/check_kicad.py . --stage format`. Do this before
  adding further symbols, wires, or generated circuitry.
- Immediately after the first minimal PCB is created, run
  `python tools/pcb_design/check_kicad.py . --stage pcb-format`. Do this before
  adding footprints, placement, routing, or zones.
- After schematic connectivity changes run
  `python tools/pcb_design/check_kicad.py . --stage schematic`.
- For a compact review artifact, export
  `python tools/pcb_design/export_electrical_manifest.py .`. Compare two
  revisions with `diff_electrical_manifest.py`; the manifest never replaces
  the KiCad schematic or ERC review.
- `review_schematic_batch.py` also requires an accepted layout plan and recorded
  visual review, validates the JSON layout manifest, and checks that every
  electrical component is assigned to one functional block.
- Prefer the one-command batch review after a schematic change:
  `python tools/pcb_design/review_schematic_batch.py .`. Keep experiments and
  disposable probes only in ignored `scratch/`, never beside authoritative files.
- After PCB changes update from schematic, refill zones, then run the same tool
  with `--stage pcb`.
- Do not advance phase with active ERC/DRC warnings. Justified exclusions must be
  explicit in KiCad and documented.

After meaningful work:

- update `docs/PROJECT_STATE.md`;
- append an event with `python tools/pcb_design/record_event.py .`;
- review `docs/LESSONS.md` and record reusable failures or preventive checks;
- commit the validated source state, then create evidence with
  `python tools/pcb_design/snapshot_project.py . --label LABEL`;
- commit the resulting snapshot evidence.

Before handoff or release, run:

`python tools/pcb_design/check_project.py . --strict` and the applicable
`check_kicad.py` gate.

Do not overwrite released hardware variants or manufacturing packages. Create a
new revision and preserve the former release.
