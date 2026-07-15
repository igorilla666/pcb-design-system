# Safe KiCad modification

## Before editing

- Identify the authoritative `.kicad_sch`, `.kicad_pcb`, and variant.
- Check Git status and preserve unrelated changes.
- Close KiCad before raw/automated file edits. An open window may overwrite the
  new file with stale in-memory content.
- Create a commit or snapshot.

## Connectivity changes

1. Change the schematic first.
2. Validate symbol pin numbers against the exact datasheet and footprint.
3. Export a netlist and run ERC.
4. Update the PCB from the schematic.
5. Place and route the affected area.
6. Remove obsolete tracks/vias and refill zones.
7. Run DRC with schematic parity.
8. Reopen in KiCad and visually inspect.

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

## Zones and net ties

- Refill zones after changes to nets, footprints, vias, clearances, or netclass.
- Inspect both layers around net ties and split planes.
- Ensure a net tie is the only deliberate connection between ground domains.
- Highlight affected nets to find stale copper that DRC may not explain clearly.

## Release

ERC/DRC success is necessary but not proof of function. Manually review power
paths, polarities, boot states, connector pinouts, logic margins, and worst-case
current before release.
