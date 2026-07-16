# Working map

Read this page first; do not load every project document at once.

1. **Schematic:** `schematic-source.json` and `schematic-layout.json`.
2. **PCB import:** minimal board → format gate → Update PCB from Schematic.
3. **Placement:** read `pcb-layout.json`, then only the constraint modules needed
   from `pcb-constraints/index.json`; the placement-ready gate requires all to
   be accepted.
4. **Routing/review:** focus on ground, netclasses, routing and power/thermal.

Record the current phase and open risks in `PROJECT_STATE.md`. This project keeps
the process version recorded at initialization; adopt later framework features
deliberately rather than changing workflows mid-revision.
