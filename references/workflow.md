# PCB workflow and gates

## Contents

1. Project opening
2. Requirements and architecture
3. Schematic gate
4. PCB gate
5. Manufacturing gate
6. Prototype gate
7. Release gate

## 1. Project opening

- Create a new repository or physical revision directory.
- Record the pcb-design-system version.
- Declare the exact required KiCad major in `docs/kicad-toolchain.json` before
  any generated or manual KiCad source is accepted.
- Acknowledge `docs/DEPENDENCIES.md` before authoritative work. Do not discover
  inputs outside the project/toolchain boundary without approval and promotion.
- Define the authoritative files and the intended production variant.
- Write safe states, environment, lifetime, assembly strategy, and budget.

## 2. Requirements and architecture

- List interfaces, simultaneous loads, rails, peak/continuous currents, cable
  lengths, and environmental limits.
- Draw the power tree and identify the lowest-rated element in every path.
- Decide grounding domains and any single-point connection before layout.
- Freeze a provisional GPIO map after checking strap/reserved pins and firmware
  support.
- Select technically valid parts before optimizing JLCPCB class or price.

## 3. Schematic gate

- After the first symbol, run `check_kicad.py . --stage format` before adding
  wires or further symbols. It must confirm that the declared KiCad toolchain
  accepts the native format without migration.
- After the first minimal board, run `check_kicad.py . --stage pcb-format`
  before adding any footprints or layout work. It must parse without migration.
- Before a readability-only schematic pass, create
  `docs/schematic-layout.json`. Declare sheet size, reading direction, grid,
  titled block rectangles, and component assignments; use it as the generator
  input so the first output has intentional visual zones. Preserve a manifest
  baseline before rearranging the layout.
- When a generator creates the schematic, declare electrical components,
  pin-to-net maps and symbol sources in `docs/schematic-source.json`; do not
  encode this project data in the generator. For a generated or assisted PCB,
  declare outline, cut-outs, approved footprint sources and placement intent in
  `docs/pcb-layout.json` before generating the board draft.
- Verify critical parts with a symbol-pin / datasheet-function / footprint-pad
  table.
- Check diode, TVS, zener, electrolytic, LED, MOSFET, relay, and connector
  polarity.
- Add local decoupling and required bulk capacitance.
- Calculate logic thresholds with min/max values and tolerances.
- Use No Connect only for deliberately unused physical pins.
- Make all wires visible and use unambiguous net names.
- Require zero ERC errors and explain all warnings.
- Run `review_schematic_batch.py` to collect the deterministic schematic gate,
  exported netlist manifest, and optional baseline diff in one report; a
  structure-only project check is not an electrical validation.
- Require the non-forced KiCad migration probe to leave its disposable copy
  unchanged; a migration prompt is a blocking format-validation failure.
- Keep exploratory scripts and temporary KiCad files under ignored `scratch/`.
- Review current paths and fault states manually.
- Open the authoritative schematic in the declared KiCad version and record a
  visual review of every block, labels, fields, and inter-block connections.

## 4. PCB gate

- Treat an automatically generated footprint placement as a draft. Check the
  declared board geometry, footprint coverage, courtyards and edge clearances
  before routing; DRC and visual review remain required before acceptance.
- Place connectors and mechanical constraints first.
- Place protection at the entry point and bypass at the IC pins.
- Route power and returns before sensitive signals.
- Keep noisy relay/switching paths away from analog and communication inputs.
- Refill zones after every relevant edit.
- Highlight changed nets and remove obsolete tracks/vias.
- Require zero DRC errors and zero unconnected pads.
- Run the deterministic PCB gate with schematic parity.
- Review both copper layers, silkscreen, polarity, pin 1, and connector mating.

## 5. Manufacturing gate

- Recheck stock and JLCPCB class immediately before ordering.
- Generate Gerber, drill, BOM, and CPL from one frozen revision.
- Separate service-fitted and manual-soldering lists.
- Check every polarized part in the assembler preview.
- Generate checksums and date/version the package.

## 6. Prototype gate

- Start with a current-limited bench supply.
- Test one source at a time and verify anti-backfeed behavior.
- Measure rails, total current, and component temperatures at worst-case load.
- Test boot/reset safe states, relays, communications, sensors, ADC calibration,
  and external peripherals.
- Perform a representative burn-in for continuous-duty products.

## 7. Release gate

- Update state, log, ADRs, pin map, limits, test results, and open risks.
- Commit the validated source state before creating a snapshot. A dirty-source
  snapshot is a non-release exception and must use `--allow-dirty`.
- Tag the tested revision.
- Never modify a released manufacturing package; create a new revision.
