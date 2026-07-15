from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from export_electrical_manifest import manifest_from_netlist  # noqa: E402


NETLIST = """<?xml version="1.0" encoding="utf-8"?>
<export>
  <components>
    <comp ref="R1"><value>10k</value><footprint>Resistor_SMD:R_0603</footprint><fields><field name="MPN">RC0603</field></fields><libsource lib="Device" part="R"/></comp>
    <comp ref="U1"><value>MCU</value><footprint>Package_QFP:LQFP-48</footprint><libsource lib="MCU" part="Chip"/></comp>
  </components>
  <nets>
    <net code="1" name="+3V3"><node ref="U1" pin="1" pinfunction="VDD" pintype="power_in"/><node ref="R1" pin="1" pinfunction="~" pintype="passive"/></net>
  </nets>
</export>
"""


class ElectricalManifestTests(unittest.TestCase):
    def test_manifest_is_compact_and_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            netlist = Path(temporary) / "sample.xml"
            netlist.write_text(NETLIST, encoding="utf-8")
            manifest = manifest_from_netlist(netlist, "sample.kicad_pro")

        self.assertEqual(manifest["summary"], {
            "components": 2,
            "nets": 1,
            "connected_components": 2,
            "connections": 2,
        })
        self.assertEqual([item["ref"] for item in manifest["components"]], ["R1", "U1"])
        self.assertEqual(manifest["components"][0]["fields"], {"MPN": "RC0603"})
        self.assertEqual(manifest["nets"][0]["nodes"][0]["ref"], "R1")
        json.dumps(manifest, sort_keys=True)

    def test_diff_reports_connection_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            netlist = root / "sample.xml"
            netlist.write_text(NETLIST, encoding="utf-8")
            before = manifest_from_netlist(netlist, "before.kicad_pro")
            after = json.loads(json.dumps(before))
            after["nets"][0]["nodes"] = after["nets"][0]["nodes"][1:]
            before_path, after_path = root / "before.json", root / "after.json"
            before_path.write_text(json.dumps(before), encoding="utf-8")
            after_path.write_text(json.dumps(after), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "diff_electrical_manifest.py"), str(before_path), str(after_path), "--fail-on-change"],
                check=False, capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("connection removed: +3V3 <- R1.1", result.stdout)


if __name__ == "__main__":
    unittest.main()
