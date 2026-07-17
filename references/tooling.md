# Reproducible tool policy

Only scripts listed as `approved` in `docs/tooling-manifest.json` may create,
transform, validate, or otherwise influence authoritative hardware. Agents must
not run an unregistered diagnostic, experiment, or historical script merely
because it exists in the repository or on the machine.

## Historical scripts

Preserve a potentially useful historical script under
`tools/pcb_design/legacy/`; do not execute it against authoritative files. Add a
`quarantined` manifest entry including its hash, origin, purpose, and the review
evidence that is still required. Evaluate it in a disposable fixture or a clean
scratch copy. Promote it only when a reviewer has recorded:

1. its purpose, inputs, outputs, and failure modes;
2. a source review for hard-coded paths, external discovery, version fallbacks,
   writes, and destructive operations;
3. deterministic tests and expected output;
4. a replacement or removal of machine-specific dependencies; and
5. a new hash and `approved` entry after moving it out of `legacy/`.

Do not silently modify a reviewed script. A changed hash requires fresh review
and a corresponding manifest update in the same commit.

## KiCad executables

`docs/kicad-toolchain.json` declares the required major. `check_kicad.py` may
use only that major: it checks an explicit `--kicad-cli`, then `PATH`, then the
standard Windows location for that *same* major. A different installed major,
including KiCad 8, is an error, never a fallback.
