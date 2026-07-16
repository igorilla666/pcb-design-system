from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SCRIPT = SCRIPTS / "check_schematic_layout_plan.py"


ACCEPTED_PLAN = """# Schematic layout plan

- Status: accepted

## Sheet and reading flow

- Sheet size: A3
- Reading direction: left to right

## Functional blocks

| ID | Function | Inputs / outputs | Planned area |
| --- | --- | --- | --- |
| PWR | Power | AC / DC | left |

## Visual review

- [x] Opened in the declared KiCad version.
- [x] Inspected labels and fields for overlaps.
- [x] Traced all inter-block connections.
"""


class SchematicLayoutPlanTests(unittest.TestCase):
    def test_accepted_plan_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / "docs"
            docs.mkdir()
            (docs / "schematic-layout.md").write_text(ACCEPTED_PLAN, encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(root)], check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_draft_plan_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / "docs"
            docs.mkdir()
            (docs / "schematic-layout.md").write_text(ACCEPTED_PLAN.replace("accepted", "draft", 1), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(root)], check=False, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("status must be accepted", result.stdout)


if __name__ == "__main__":
    unittest.main()
