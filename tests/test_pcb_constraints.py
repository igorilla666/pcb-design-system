from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "project-template"
SCRIPT = ROOT / "scripts" / "check_pcb_constraints.py"


class PCBConstraintTests(unittest.TestCase):
    def run_check(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(SCRIPT), str(root), *args], check=False, capture_output=True, text=True)

    def test_planned_modules_are_complete_but_not_placement_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copytree(TEMPLATE / "docs", root / "docs")
            planned = self.run_check(root)
            ready = self.run_check(root, "--require-placement-ready")
        self.assertEqual(planned.returncode, 0, planned.stdout + planned.stderr)
        self.assertNotEqual(ready.returncode, 0)
        self.assertIn("constraint not accepted", ready.stdout)
