from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check_kicad.py"
PROJECT_ENV = "PCB_DESIGN_KICAD_PROJECT"


@unittest.skipUnless(os.getenv(PROJECT_ENV), f"set {PROJECT_ENV} to run KiCad integration tests")
class KiCadIntegrationTests(unittest.TestCase):
    def test_declared_project_passes_its_first_file_format_gates(self) -> None:
        project = Path(os.environ[PROJECT_ENV]).expanduser().resolve()
        self.assertTrue((project / "docs" / "kicad-toolchain.json").is_file())
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            for stage in ("format", "pcb-format"):
                result = subprocess.run(
                    [sys.executable, str(CHECK), str(project), "--stage", stage, "--output-dir", str(output)],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
