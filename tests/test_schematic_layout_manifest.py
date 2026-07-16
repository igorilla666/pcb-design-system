from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SCRIPT = SCRIPTS / "check_schematic_layout_manifest.py"


def manifest() -> dict:
    return {
        "status": "accepted",
        "generation": {"mode": "manual", "source": None},
        "sheet": {"size": "A3", "orientation": "landscape", "grid_mm": 1.27, "reading_flow": "left-to-right"},
        "blocks": [
            {"id": "power", "title": "Power", "bounds_mm": [12.7, 12.7, 50.8, 50.8], "components": ["R1"]},
            {"id": "logic", "title": "Logic", "bounds_mm": [76.2, 12.7, 50.8, 50.8], "components": ["U1"]},
        ],
        "visual_review": ["opened in KiCad", "checked labels", "traced inter-block nets"],
    }


class SchematicLayoutManifestTests(unittest.TestCase):
    def test_accepted_manifest_covers_components(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / "docs"
            docs.mkdir()
            (docs / "schematic-layout.json").write_text(json.dumps(manifest()), encoding="utf-8")
            electrical = root / "electrical.json"
            electrical.write_text(json.dumps({"components": [{"ref": "R1"}, {"ref": "U1"}]}), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(root), "--require-accepted", "--electrical-manifest", str(electrical)],
                check=False, capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("blocks=2; components=2", result.stdout)

    def test_overlap_or_missing_component_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / "docs"
            docs.mkdir()
            data = manifest()
            data["blocks"][1]["bounds_mm"] = [50.8, 12.7, 50.8, 50.8]
            (docs / "schematic-layout.json").write_text(json.dumps(data), encoding="utf-8")
            electrical = root / "electrical.json"
            electrical.write_text(json.dumps({"components": [{"ref": "R1"}, {"ref": "U1"}, {"ref": "C1"}]}), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(root), "--require-accepted", "--electrical-manifest", str(electrical)],
                check=False, capture_output=True, text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("functional blocks overlap", result.stdout)
        self.assertIn("components missing from layout blocks: C1", result.stdout)


if __name__ == "__main__":
    unittest.main()
