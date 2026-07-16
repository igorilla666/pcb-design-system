# Framework test method

Run one command from the framework root:

`python scripts/test_framework.py --suite all`

It writes a concise ignored report to `build/framework-test/summary.txt`.

| Suite | What it proves | Normal use |
| --- | --- | --- |
| `fast` | Pure logic, policies, parsers and deterministic transforms. | Every edit. |
| `template` | A fresh project has the expected records, tools and contracts. | Template/process changes. |
| `fixtures` | Known past failures remain detected. | Every bug fix. |
| `kicad` | Real KiCad format gates on a declared project. | On a KiCad-equipped machine. |

The KiCad suite is intentionally skipped unless `PCB_DESIGN_KICAD_PROJECT` names
a project with its exact toolchain declared. It never tries a different KiCad
major and writes evidence only to a temporary directory.

When a real failure occurs, add the smallest fixture under `tests/fixtures/`, a
focused test, and a changelog entry. Do not use an external project, a live KiCad
library, or chat history as the fixture source.
