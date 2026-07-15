# Reusable lessons from Water Controller

- Zero DRC errors did not reveal reversed relay flyback diodes, swapped WS2812
  supply pins, marginal RS-485 logic levels, or incorrect comparator feedback.
- Treat symbol pin, datasheet function, and footprint pad as a single contract.
- Qualify references by board when discussing modules: `D1@controller` and
  `D1@module` are different parts.
- A manufacturer schematic may contain a wrong value. Measure the board, read the
  exact datasheet, and obtain written vendor confirmation for critical limits.
- A continuity beep can be diode conduction; measure both directions and read the
  displayed value.
- Rail limits are not additive. Follow source, diode, regulator, PTC, trace, and
  connector; the lowest safe limit governs.
- Separate positive supplies may share data only with a common reference ground.
  Use isolation/differential signaling if grounds must remain separate.
- Define ground domains and the star point before routing.
- Place 100 nF bypass capacitors at IC supply pins, not merely on the same net.
- Calculate logic compatibility with VOH/VOL and VIH/VIL limits plus tolerances.
- Freeze firmware GPIO mapping from the final schematic, not a breadboard map.
- Do not hide wires with transparent colors; graphical visibility is not
  electrical connectivity.
- Close KiCad, snapshot, edit schema first, update PCB, refill zones, validate, and
  record the result.
- Choose technically correct components before optimizing Basic/Preferred status.
- Keep baseline, variants, and manufacturing packages physically independent.
