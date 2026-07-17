from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "assets" / "project-template" / "docs"


class GeneratorContractTemplateTests(unittest.TestCase):
    def test_generator_inputs_are_present_and_identified(self) -> None:
        schematic = json.loads((DOCS / "schematic-source.json").read_text(encoding="utf-8"))
        pcb = json.loads((DOCS / "pcb-layout.json").read_text(encoding="utf-8"))
        self.assertEqual(schematic["format"], "pcb-design-system/schematic-source/v1")
        self.assertEqual(schematic["status"], "planned")
        self.assertEqual(pcb["format"], "pcb-design-system/pcb-layout/v2")
        self.assertEqual(pcb["status"], "planned")
        self.assertEqual(pcb["generation"]["mode"], "manual")
        self.assertEqual(pcb["board_source"]["mode"], "update-from-schematic")
        self.assertEqual(pcb["constraints_index"], "docs/pcb-constraints/index.json")

    def test_project_process_map_is_present(self) -> None:
        process = (DOCS / "PROCESS.md").read_text(encoding="utf-8")
        self.assertIn("pcb-constraints/index.json", process)
        italian = (DOCS / "PROCESS.it.md").read_text(encoding="utf-8")
        self.assertIn("pcb-constraints/index.json", italian)
