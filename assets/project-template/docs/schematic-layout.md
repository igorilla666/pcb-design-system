# Schematic layout plan

- Status: draft
- Authoritative schematic: not created
- Layout pass: not started
- Canonical geometry: `docs/schematic-layout.json`

## Sheet and reading flow

- Sheet size: select before the readability pass.
- Reading direction: power/input at left or top; loads and external interfaces at right or bottom.
- Grid and spacing: state the chosen grid and minimum separation between functional blocks.

## Functional blocks

| ID | Function | Inputs / outputs | Planned area |
| --- | --- | --- | --- |
| | | | |

## Visual rules

- Use one titled boundary per functional block; do not use boxes as electrical connections.
- Keep block titles, reference/value fields, net labels, and wires legible without overlap.
- Use clear local labels or hierarchical connections rather than long ambiguous wires.
- Preserve the electrical netlist while performing a readability-only layout pass.

## Visual review

- [ ] Open the authoritative schematic in the declared KiCad version.
- [ ] Inspect every block at a readable zoom for overlaps, clipped text, and ambiguous labels.
- [ ] Confirm all inter-block connections and power flow can be followed without relying on coordinates.
- [ ] Record the reviewer, date, and evidence (PDF, screenshot, or KiCad review note).
