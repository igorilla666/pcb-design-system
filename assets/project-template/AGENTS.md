# PCB project agent instructions

Use repository files and Git as the source of truth. Do not rely on chat history
for project state, decisions, risks, tests, or release status.

Before changing hardware:

1. Read `docs/PROJECT_STATE.md` and the latest `docs/PROJECT_LOG.md` entries.
2. Read applicable ADRs in `docs/decisions/`.
3. Check `git status` and preserve unrelated changes.
4. Identify the authoritative schematic, PCB, revision, and production variant.
5. Close KiCad before editing `.kicad_*` files outside KiCad.

Apply schematic changes first. Verify symbol pin, datasheet function, and
footprint pad as one contract. Store any generator used for authoritative KiCad
files in this repository; do not rely on agent scratch files.

Required gates:

- `check_project.py --strict` checks records only; never call it electrical proof.
- After schematic connectivity changes run
  `python tools/pcb_design/check_kicad.py . --stage schematic`.
- After PCB changes update from schematic, refill zones, then run the same tool
  with `--stage pcb`.
- Do not advance phase with active ERC/DRC warnings. Justified exclusions must be
  explicit in KiCad and documented.

After meaningful work:

- update `docs/PROJECT_STATE.md`;
- append an event with `python tools/pcb_design/record_event.py .`;
- create evidence with `python tools/pcb_design/snapshot_project.py . --label LABEL`;
- review `docs/LESSONS.md` and record reusable failures or preventive checks;
- commit one coherent change.

Before handoff or release, run:

`python tools/pcb_design/check_project.py . --strict` and the applicable
`check_kicad.py` gate.

Do not overwrite released hardware variants or manufacturing packages. Create a
new revision and preserve the former release.
