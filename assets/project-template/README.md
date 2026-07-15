# {{PROJECT_NAME}}

PCB project initialized on {{DATE}} with pcb-design-system {{SYSTEM_VERSION}}.
The repository includes model-neutral agent instructions and local workflow
tools, so its records remain usable across supported AI coding agents.

## Start here

1. Read `docs/PROJECT_STATE.md`.
2. Complete requirements, power budget, pin map, and component register.
3. Record architecture decisions in `docs/decisions/`.
4. Keep `docs/PROJECT_LOG.md` append-only.
5. Use `docs/RELEASE_CHECKLIST.md` before manufacturing.
6. Run `check_project.py --strict` for records and `check_kicad.py` for electrical
   gates before handoff.
7. Prefer `review_schematic_batch.py` after schematic changes; use ignored
   `scratch/` only for temporary probes.
8. Set `docs/kicad-toolchain.json` to the exact KiCad major before creating
   hardware; validation rejects an undeclared or mismatched toolchain.
9. After the first symbol, run `check_kicad.py . --stage format` before growing
   the schematic.
10. After the first minimal board, run `check_kicad.py . --stage pcb-format`
    before placement or routing.

## Layout

- `hardware/`: authoritative KiCad sources and independent revisions.
- `manufacturing/`: immutable release packages, one directory per revision.
- `docs/`: state, log, decisions, calculations, tests, and validation evidence.
- `tools/`: project-specific validation scripts.
- `scratch/`: ignored, disposable diagnostics only; never authoritative output.
- `AGENTS.md`: authoritative model-neutral working instructions.
- `CLAUDE.md` and `GEMINI.md`: thin pointers to the common instructions.

Do not overwrite a released variant or manufacturing package. Create a new
revision.
