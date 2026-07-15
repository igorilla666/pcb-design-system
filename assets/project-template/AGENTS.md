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

Apply schematic changes first. Verify symbol pin, datasheet function, and
footprint pad as one contract. Store any generator used for authoritative KiCad
files in this repository; do not rely on agent scratch files.

Required gates:

- `check_project.py --strict` checks records only; never call it electrical proof.
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
