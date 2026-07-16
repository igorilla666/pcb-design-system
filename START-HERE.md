# Start here

You do not need to read the whole framework. This page is the operational map.

## The essential flow

1. Declare the exact KiCad version and keep sources portable.
2. Build and validate the schematic first.
3. Create a minimal PCB, validate its format, then use KiCad to update it from
   the schematic.
4. Before placement, accept the modular constraints and run the placement gate.
5. Place, inspect provisional ground zones, route, then run DRC and manual
   review.

## What to read, when

| When you are… | Read only… |
| --- | --- |
| Starting/resuming a project | Project `AGENTS.md`, `PROJECT_STATE.md`, latest log. |
| Building the schematic | `schematic-source.json`, `schematic-layout.json`. |
| Preparing placement | `pcb-layout.json`, then the relevant files named by `pcb-constraints/index.json`. |
| Routing or reviewing copper | `ground.json`, `netclasses.json`, `routing.json`, `power-thermal.json`. |
| Checking a framework update | `CHANGELOG.md`, newest entry only. |

## Rules that are never optional

- Use the declared KiCad major; never fall back to another one.
- Schema first; KiCad imports the footprints/nets into the PCB.
- No unreviewed historical scripts or machine-local discovery.
- No placement until the constraint gate passes.
- DRC is necessary, but manual electrical and mechanical review remains required.

## Keeping control

Treat the framework as a checklist, not as one prompt. Work one phase at a time,
open only the records for that phase, and finish by recording the decision and
validation result. Existing projects remain on their recorded process version;
adopt a newer capability deliberately, one module at a time.
