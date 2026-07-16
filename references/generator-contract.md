# Declarative generator contract

Do not make a project-specific Python list the source of truth for a generated
schematic or PCB. The generator must consume small, reviewed repository inputs
and write only the declared output. This separates electrical intent from
visual geometry and avoids rediscovering symbols, footprints, or coordinates
from another project or a machine-local installation.

## Schematic inputs

For a generated schematic, use both `docs/schematic-source.json` (electrical
intent) and `docs/schematic-layout.json` (sheet geometry and readable functional
blocks). The source file declares, per component, reference, library ID, value,
footprint, approved fields, pin-to-net map, and symbol definition source.

A generator may read a standard symbol only from the declared KiCad major; a
custom or frozen symbol must be promoted into the repository and recorded in
`DEPENDENCIES.md`. The generated schematic must embed the exact symbol
definitions it used. It must not invent pin numbers, net names, no-connect
markers, properties, or coordinates. It may derive label coordinates from a
reviewed pin geometry only. Validate after one representative symbol, then after
the complete schematic with ERC and the electrical manifest.

## PCB inputs

For a generated or assisted PCB, keep `docs/pcb-layout.json` small: it names the
schematic-imported board, constraint index, output and placement records. Exact
outline/cut-outs, manufacturing stackup, netclasses, ground continuity, zones,
routing, power/thermal and assembly/test data live in independent files under
`docs/pcb-constraints/`. The generator loads only the modules relevant to the
operation, but it may not place a component until all are accepted. It must not
route, silently skip a missing footprint, choose a fallback KiCad version/library,
or declare placement ready when checks fail.

The PCB must first be created as a minimal native board and pass the format gate.
Then invoke KiCad's **Update PCB from Schematic** operation. Only after that
import may a placement generator move the imported footprints. A generator must
never load footprints from a library and recreate reference/net associations on
its own: the schematic is the authoritative footprint assignment and KiCad is
the authoritative transfer mechanism.

## Required generator behaviour

1. Accept explicit input/output paths; never hard-code a revision, product,
   `C:` path, or design coordinates in source code.
2. Use only the exact declared KiCad major and fail if a declared asset cannot
   be resolved.
3. Confirm that the declared board source is `update-from-schematic`; fail if
   the schematic lacks a footprint assignment or if the import has not occurred.
4. Require accepted modular PCB constraints before placement; report netclass
   corridor, plane split, slot, keep-out and return-path risks.
5. Produce deterministic order and a report with input hashes, component count,
   output path and toolchain version.
6. Live in `tools/pcb_design/generators/`, be registered in the tooling manifest,
   and pass a small fixture test before affecting authoritative hardware.
7. Keep design-specific JSON and custom assets in the project repository, never
   as opaque Python literals.

The framework deliberately provides contracts and gates, not a universal raw
S-expression writer. Generation is accepted only after normal format, ERC/DRC
and visual-review gates.
