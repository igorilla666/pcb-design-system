# Release checklist

## Sources and state

- [ ] `python tools/pcb_design/check_project.py . --strict` passes.
- [ ] Applicable `check_kicad.py` schematic and PCB gates pass.
- [ ] Authoritative revision and files recorded in PROJECT_STATE.
- [ ] Git working tree reviewed.
- [ ] Requirements, power budget, pin map, and ADRs current.

## Schematic

- [ ] Critical symbol/datasheet/footprint mappings verified.
- [ ] Polarities and boot-safe states reviewed.
- [ ] Local decoupling present.
- [ ] Logic levels checked at worst case.
- [ ] ERC has zero active errors or warnings; exclusions are documented.
- [ ] Netlist and current paths manually reviewed.

## PCB

- [ ] DRC has zero active errors or warnings and zero unconnected pads.
- [ ] Zones refilled and split grounds/net ties reviewed on both layers.
- [ ] Stale tracks/vias removed.
- [ ] Pin 1, polarity, connectors, silkscreen, and mechanical access checked.

## Sourcing and manufacturing

- [ ] MPN, footprint, LCSC, and stock rechecked.
- [ ] Gerber, drill, BOM, and CPL come from one frozen revision.
- [ ] Manual assembly list separated.
- [ ] Assembly preview and rotations checked.
- [ ] Checksums generated.

## Prototype

- [ ] First-power and worst-case load tests passed.
- [ ] Thermal and burn-in results recorded.
- [ ] Firmware safe states and pin map verified.
- [ ] Open risks explicitly accepted.

## Release

- [ ] Validation snapshot stored.
- [ ] Changelog updated.
- [ ] Git tag/release created.
- [ ] Manufacturing package made immutable.
