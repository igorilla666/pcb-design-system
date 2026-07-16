# Changelog

This is a human summary. Read the newest entry; older entries are context, not
mandatory homework.

## 1.7.0 — Modular pre-placement constraints

- PCB constraints are eight small files, indexed by one short file.
- Netclasses, stackup, ground, mechanics, routing, thermal and test constraints
  must be accepted before placement.
- `check_pcb_constraints.py . --require-placement-ready` is the placement gate.

## 1.6.0 — Ground continuity before placement

- Plan reference layers, ground domains, safety keep-outs and return paths before
  placing components; inspect provisional zones after placement.

## 1.5.0 — PCB starts from schematic import

- Create/validate a minimal board, then use KiCad Update PCB from Schematic.
- Automation places imported footprints only; it never rebuilds mappings.

## 1.4.0 — Declarative generator inputs

- Separate electrical source, schematic layout and PCB placement inputs so a
  generator does not hide project decisions in Python code.

## 1.3.0 — Reproducible tools and KiCad version

- Only hash-recorded project tools may affect hardware.
- Historical scripts are quarantined; KiCad uses the declared major exactly.

## 1.2.0 and earlier — Foundation

- Git-backed project records, dependency boundary, KiCad format gates, electrical
  manifest and schematic readability review.
