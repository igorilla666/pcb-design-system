# PCB project agent instructions

Use repository files and Git as the source of truth. Do not rely on chat history
for project state, decisions, risks, tests, or release status.

Before changing hardware:

1. Read `docs/PROJECT_STATE.md` and the latest `docs/PROJECT_LOG.md` entries.
2. Read applicable ADRs in `docs/decisions/`.
3. Check `git status` and preserve unrelated changes.
4. Identify the authoritative schematic, PCB, revision, and production variant.
5. Close KiCad before editing `.kicad_*` files outside KiCad.

Apply schematic changes first, update the PCB from the schematic, refill zones,
then run ERC and DRC. Verify symbol pins, datasheet functions, and footprint pads
as one contract. ERC/DRC success is necessary but is not functional proof.

After meaningful work:

- update `docs/PROJECT_STATE.md`;
- append an event with `python tools/pcb_design/record_event.py .`;
- create evidence with `python tools/pcb_design/snapshot_project.py . --label LABEL`;
- commit one coherent change.

Before handoff or release, run:

`python tools/pcb_design/check_project.py . --strict`

Do not overwrite released hardware variants or manufacturing packages. Create a
new revision and preserve the former release.
