# Dependency contract

- Status: pending

## Allowed sources

1. Files inside this repository.
2. The KiCad toolchain declared in `docs/kicad-toolchain.json`.
3. Dependencies recorded and promoted in the ledger below.

## Prohibited discovery

- Do not scan, search, or reuse files from adjacent repositories, home folders,
  drives, cloud folders, or prior projects without explicit user authorization.
- Do not infer KiCad syntax from arbitrary local files.
- Do not make an authoritative output depend on a private scratch file or a
  machine-specific path.

## Dependency ledger

| ID | Type | Source and provenance | Version | License | SHA-256 | Promoted repository path | User approval |
| --- | --- | --- | --- | --- | --- | --- | --- |
| none | — | No external dependency promoted. | — | — | — | — | — |

## Promotion procedure

Before using an external resource, stop and record why it is needed. Obtain
explicit user approval, then copy only the necessary asset or reusable code into
this repository, record its provenance/license/hash above, add a deterministic
test, and commit it before using it for authoritative hardware.
