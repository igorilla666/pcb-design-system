# Portable dependency policy

The default execution boundary is the current project repository. Agents may
also use the KiCad toolchain declared by the project. They must not scan local
drives, adjacent repositories, prior projects, home directories, or cloud shares
to discover syntax, code, symbols, or templates.

When an external resource is genuinely needed, stop before reading or using it.
Record the source, reason, exact version, license, hash, intended repository
path, and user approval in `docs/DEPENDENCIES.md`. Promote only the minimum
necessary material into the project or central design system, test it, and
commit it. A toolchain dependency is not a license to copy an entire live KiCad
library into a project.

Use the project-local symbol/footprint library for custom or vendored assets.
Standard component/footprint choices, including relay footprints, are project
decisions supported by BOM evidence and ADRs; they are never framework defaults.
