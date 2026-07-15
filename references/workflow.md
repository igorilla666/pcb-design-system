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

- Verify critical parts with a symbol-pin / datasheet-function / footprint-pad
  table.
- Check diode, TVS, zener, electrolytic, LED, MOSFET, relay, and connector
  polarity.
- Add local decoupling and required bulk capacitance.
- Calculate logic thresholds with min/max values and tolerances.
- Use No Connect only for deliberately unused physical pins.
- Make all wires visible and use unambiguous net names.
- Require zero ERC errors and explain all warnings.
- Review current paths and fault states manually.

## 4. PCB gate

- Place connectors and mechanical constraints first.
- Place protection at the entry point and bypass at the IC pins.
- Route power and returns before sensitive signals.
- Keep noisy relay/switching paths away from analog and communication inputs.
- Refill zones after every relevant edit.
- Highlight changed nets and remove obsolete tracks/vias.
- Require zero DRC errors and zero unconnected pads.
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
- Tag the tested revision.
- Never modify a released manufacturing package; create a new revision.
