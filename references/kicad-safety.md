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

Run `check_kicad.py` after connectivity changes. Active warnings, failed netlist
export, multi-pin components with no net connections, or a missing `.kicad_pro`
block the gate. Exclude a justified warning in KiCad and document why; never
classify warning families as harmless without inspecting each instance.

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
