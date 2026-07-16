# PCB Design System

A reusable, Git-backed workflow for designing, reviewing, and releasing KiCad
PCB projects with AI coding agents. It keeps requirements, decisions, project
state, validation evidence, and manufacturing releases in the repository instead
of relying on chat history.

## Highlights

- Compatible with OpenAI Codex, Claude Code, Gemini CLI, and Antigravity.
- Provides a ready-to-use PCB project structure and release checklist.
- Records decisions, risks, component choices, ERC/DRC results, and snapshots.
- Includes lessons learned from a real water-controller PCB project.
- Exports compact electrical manifests from KiCad netlists for focused review
  and semantic diffs, without making generated artifacts authoritative.

## Orientation

Start with [START-HERE.md](START-HERE.md): it is the one-page operational map.
Use [CHANGELOG.md](CHANGELOG.md) to understand only the newest framework changes.

## Install

Requires Python 3 and Git.

```bash
git clone https://github.com/igorilla666/pcb-design-system.git
cd pcb-design-system
python scripts/install_skill.py --platform all
```

Then ask your agent to use `pcb-design-system` when starting or resuming a PCB
project.

## Start a project

On Windows, open `launcher/PCBProjectLauncher.exe`. The graphical launcher lets
you choose the destination, GitHub visibility, and whether to continue in
ChatGPT/Codex or Gemini/Antigravity. Both choices use the same agent-neutral
project records.

For a terminal or non-Windows environment, run:

```bash
python scripts/new_project.py
```

The launcher asks for the exact destination folder and defaults to a private
GitHub repository. Authenticate once with `gh auth login`, `GH_TOKEN`, or
`git credential-manager github login`. Use `--dry-run` to preview or
`--no-github` only for an intentionally offline project.

To rebuild the Windows executable from source:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows_launcher.ps1
```

See [`SKILL.md`](SKILL.md) for the workflow and
[`references/compatibility.md`](references/compatibility.md) for platform paths.

## Compact electrical reviews

After a schematic change and its ERC gate, create a deterministic review view:

```bash
python tools/pcb_design/export_electrical_manifest.py .
```

Compare artifacts from two revisions with:

```bash
python tools/pcb_design/diff_electrical_manifest.py before.json after.json
```

The output summarizes components, fields, footprints, nets, and pin-to-net
connections. It is a review aid; the KiCad schematic and exported netlist are
still authoritative.

For the normal schematic review path, prefer one batch command. It runs the
schematic gate, exports the manifest, optionally compares a baseline, and writes
one report under `build/pcb-design-check/`:

```bash
python tools/pcb_design/review_schematic_batch.py . --baseline docs/validation/previous/electrical-manifest.json
```

Use ignored `scratch/` only for disposable probes. Commit validated sources
before `snapshot_project.py`; snapshots reject a dirty source worktree unless
`--allow-dirty` explicitly records a non-release exception.

Every project declares its required KiCad major in
`docs/kicad-toolchain.json`. The electrical gate rejects an undeclared or
mismatched CLI, checks the schematic generator major, and fails if KiCad's
non-forced upgrade command would migrate a disposable copy of a source file.
Run `check_kicad.py . --stage format` immediately after the first symbol, before
the schematic becomes expensive to regenerate.
Run `check_kicad.py . --stage pcb-format` immediately after creating the first
minimal board, before adding layout work.

After that gate, use KiCad's Update PCB from Schematic operation. It imports the
approved footprint/reference/net mapping; automation may place those footprints
but must not recreate them from libraries.

Before placement, accept the modular records listed by
`docs/pcb-constraints/index.json`, including stackup, netclasses, mechanical
space, ground, routing, thermal and assembly constraints, then run the
placement-ready constraint gate. This keeps each LLM interaction focused on one
small domain rather than a monolithic PCB plan.

For readable schematics, make `docs/schematic-layout.json` the generator input:
it records the sheet, grid, block bounds, titles, and component assignments.
Record the human visual review in `docs/schematic-layout.md`. The batch review
requires both and verifies that every electrical component belongs to one block;
ERC success by itself is not a documentation review.

Generated designs use declarative inputs rather than a project-specific Python
list: `docs/schematic-source.json` records electrical intent and approved symbol
sources, while `docs/pcb-layout.json` records the board source and placement
intent. PCB constraints are split into small files under
`docs/pcb-constraints/`. See
[`references/generator-contract.md`](references/generator-contract.md).

Every project also carries `docs/DEPENDENCIES.md`: it limits normal work to the
repository and declared KiCad toolchain. External code or assets require user
approval, provenance, version, license, hash, promotion path, and a test before
they can affect authoritative hardware.

Project tools are controlled too: `docs/tooling-manifest.json` lists the
reviewed, hash-recorded scripts allowed to affect hardware. Historical
diagnostics remain quarantined until tested and promoted. KiCad selection is
exact: a project declared for KiCad 10 fails if only KiCad 8 is available; the
framework never falls back to another major.

## License

Licensed under the [Apache License 2.0](LICENSE). The launcher source and bundled
icon carry the same license; the Windows executable includes license metadata and
the complete license text as an embedded resource.
