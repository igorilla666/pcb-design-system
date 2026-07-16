# Modular PCB pre-placement constraints

Do not give an LLM one large PCB-planning document. `docs/pcb-constraints/index.json`
is a compact map; it points to eight independent modules. Read the index first,
then load only the modules relevant to the current decision. Before any component
placement, complete all modules, mark each `accepted`, and run:

`python tools/pcb_design/check_pcb_constraints.py . --require-placement-ready`

Each accepted module needs a concise `decision_summary`. It may say that a
feature is not applicable, but must say why; this avoids fake placeholder holes,
fiducials or zones while retaining an auditable decision.

| Module | Purpose |
| --- | --- |
| `mechanical` | Outline, holes, cut-outs, connector access, height limits. |
| `manufacturing` | Stackup and confirmed fabricator limits. |
| `netclasses` | Width, clearance, via and net assignments. |
| `ground` | Reference layers, domains, continuity, safety keep-outs, return paths. |
| `zones` | Functional placement areas and isolation boundaries. |
| `routing` | Preferred layers, via policy, critical/differential routing constraints. |
| `power-thermal` | Current paths, copper needs, thermal and derating constraints. |
| `assembly-test` | Fiducials, test/programming access and orientation rules. |

Netclasses are not a late routing detail. Define them before placement, using
real fabricator limits and safety requirements, so component spacing reserves
the required track/clearance corridors. The ground plan is likewise pre-placement
intent: inspect provisional zones after placement and again after routing.

`pcb-layout.json` is deliberately small: it names the schematic-imported board,
the constraints index, and the final placement records. It must not duplicate the
details held by the modules.
