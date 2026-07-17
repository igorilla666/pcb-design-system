from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


class RegressionFixtureTests(unittest.TestCase):
    def test_fixture_inventory_is_documented(self) -> None:
        self.assertTrue((FIXTURES / "README.md").is_file())
        self.assertTrue((FIXTURES / "pcb" / "root-uuid.kicad_pcb").is_file())
