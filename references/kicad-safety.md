# Safe KiCad modification

## Before editing

- Identify the authoritative `.kicad_sch`, `.kicad_pcb`, and variant.
- Read `docs/kicad-toolchain.json` and confirm that the installed `kicad-cli`
  major matches it before editing or generating files.
- Check Git status and preserve unrelated changes.
- Close KiCad before raw/automated file edits. An open window may overwrite the
  new file with stale in-memory content.
- Create a commit or snapshot.

## First-symbol format gate

Immediately after the first symbol is placed or generated, and before adding
other symbols or any wires, run:

`python tools/pcb_design/check_kicad.py . --stage format`

This performs only toolchain, header, and non-forced migration checks; it does
not require a complete circuit or ERC-clean schematic. A failure means correct
the project/generator format first, then restart from that small source state.

## First-board format gate

Immediately after the first minimal PCB is created or generated, and before
adding footprints, placement, routing, or zones, run:

`python tools/pcb_design/check_kicad.py . --stage pcb-format`

This validates the native board syntax with KiCad's non-forced migration probe
without requiring an outline or a DRC-clean layout.

After this gate, invoke KiCad's Update PCB from Schematic operation. This is the
only permitted transfer of references, footprint assignments and nets to a
board. Agents and generators may place the imported footprints, but must never
reconstruct them directly from a library.

Before placement, accept all modules listed by
`docs/pcb-constraints/index.json`, then run the placement-ready constraint gate.
It records netclasses, stackup, mechanical/safety space, ground continuity,
routing, thermal and assembly constraints as small independent files. Use
provisional zones after placement to expose fragmented planes or isolated
islands; refill and review again after routing.

## Connectivity changes

1. Change the schematic first.
2. Validate symbol pin numbers against the exact datasheet and footprint.
3. Export a netlist and run ERC. Export an electrical manifest when a compact,
   reviewable record of components and pin-to-net connections is useful.
4. Update the PCB from the schematic.
5. Place and route the affected area.
6. Remove obsolete tracks/vias and refill zones.
7. Run DRC with schematic parity.
8. Reopen in KiCad and visually inspect.

Run `check_kicad.py` after connectivity changes. Active warnings, failed netlist
export, multi-pin components with no net connections, or a missing `.kicad_pro`
block the gate. Exclude a justified warning in KiCad and document why; never
classify warning families as harmless without inspecting each instance.

`export_electrical_manifest.py` and `diff_electrical_manifest.py` summarize an
exported netlist and its changes. They are intentionally read-only review aids:
they neither edit KiCad files nor prove an electrical design correct.

## Readability-only layout passes

Keep the electrical manifest as a baseline, then record the intended sheet,
reading flow, grid, block rectangles, and component assignments in
`docs/schematic-layout.json`. Generators must consume that manifest rather than
hard-code scattered geometry. A visual layout change must preserve the intended
netlist; run the batch review after it. Do not accept a zero-ERC result as proof
that a reviewer can read the schematic: inspect it in the declared KiCad version
and record the completed visual review in `schematic-layout.md` and the JSON
manifest.

For generated hardware, keep electrical source data in
`docs/schematic-source.json` and PCB geometry/placement data in
`docs/pcb-layout.json`. The generator code must remain generic; a hard-coded
project component list, board outline or revision path is not an authoritative
input. Missing symbols or footprints are failures, never a reason to silently
select another installed KiCad library or major version.

Do not infer file compatibility from a date-format token or from a generator
claim. The declared toolchain and a successful parse by that exact `kicad-cli`
are the compatibility proof. A file that fails to load is malformed or
incompatible even if its header appears plausible.

The KiCad gate also runs `sch upgrade` or `pcb upgrade` without `--force` on a
copy under `build/`. If KiCad changes the copy, the source requires migration:
open and save it in the declared toolchain, then rerun the gate. Never use an
upgrade command directly on authoritative sources as a validation shortcut.

Do not fix a pin-pad mismatch by rotating artwork or moving labels. Correct the
symbol/footprint mapping.

## Raw file editing

Prefer KiCad GUI or KiCad CLI. When raw editing is necessary:

- keep the patch minimal;
- never rewrite the whole file for a small change;
- preserve UUIDs unless intentionally creating objects;
- validate parentheses/format and reopen the file;
- compare schema/PCB parity;
- restore immediately if the result is structurally uncertain.
- keep the generator or transformer in the project repository before accepting
  its output;
- do not validate connectivity with coordinate or overlap heuristics: the
  exported netlist is authoritative.

## Zones and net ties

- Refill zones after changes to nets, footprints, vias, clearances, or netclass.
- Inspect both layers around net ties and split planes.
- Ensure a net tie is the only deliberate connection between ground domains.
- Highlight affected nets to find stale copper that DRC may not explain clearly.

## Release

ERC/DRC success is necessary but not proof of function. Manually review power
paths, polarities, boot states, connector pinouts, logic margins, and worst-case
current before release.
