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

For a generated or assisted PCB, use `docs/pcb-layout.json`. It records the
exact outline and cut-outs, mechanical holes, isolation slots, clearance rules,
each reference's approved footprint/source, and the placement zone, coordinate,
rotation and side. The generator may initialize a minimal native board and place
approved footprints. It must not route, silently skip a missing footprint,
choose a fallback KiCad version/library, or declare placement ready when checks
fail. Generated placement is a draft until the placement gate and human review.

## Required generator behaviour

1. Accept explicit input/output paths; never hard-code a revision, product,
   `C:` path, or design coordinates in source code.
2. Use only the exact declared KiCad major and fail if a declared asset cannot
   be resolved.
3. Produce deterministic order and a report with input hashes, component count,
   output path and toolchain version.
4. Live in `tools/pcb_design/generators/`, be registered in the tooling manifest,
   and pass a small fixture test before affecting authoritative hardware.
5. Keep design-specific JSON and custom assets in the project repository, never
   as opaque Python literals.

The framework deliberately provides contracts and gates, not a universal raw
S-expression writer. Generation is accepted only after normal format, ERC/DRC
and visual-review gates.
