from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_kicad import board_has_root_uuid, find_cli, migration_probe, required_major, schematic_generator_major  # noqa: E402
from export_electrical_manifest import find_cli as manifest_cli  # noqa: E402


class KiCadToolchainTests(unittest.TestCase):
    def test_requires_declared_positive_major(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / "docs"
            docs.mkdir()
            declaration = docs / "kicad-toolchain.json"
            declaration.write_text(json.dumps({"required_major": 10}), encoding="utf-8")
            self.assertEqual(required_major(root), 10)
            declaration.write_text(json.dumps({"required_major": 0}), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "positive integer"):
                required_major(root)

    def test_reads_schematic_generator_major(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            schematic = Path(temporary) / "board.kicad_sch"
            schematic.write_text('(kicad_sch\n (generator_version "10.0")\n)\n', encoding="utf-8")
            self.assertEqual(schematic_generator_major(schematic), 10)

    def test_migration_probe_rejects_a_changed_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "board.kicad_sch"
            source.write_text("authoritative\n", encoding="utf-8")

            with patch("check_kicad.run", return_value=SimpleNamespace(returncode=0, stdout="", stderr="")):
                self.assertIsNone(migration_probe(Path("fake-cli"), "sch", source, root))

            def changes_copy(command: list[str]) -> SimpleNamespace:
                Path(command[-1]).write_text("upgraded\n", encoding="utf-8")
                return SimpleNamespace(returncode=0, stdout="upgraded", stderr="")

            with patch("check_kicad.run", side_effect=changes_copy):
                failure = migration_probe(Path("fake-cli"), "sch", source, root)
            self.assertIn("requires a KiCad sch format migration", failure)

    def test_cli_selection_never_accepts_a_wrong_major(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            cli = Path(temporary) / "kicad-cli.exe"
            cli.write_text("placeholder", encoding="utf-8")
            with patch("check_kicad.cli_major", return_value=8):
                with self.assertRaisesRegex(RuntimeError, "do not fall back"):
                    find_cli(cli, 10)
            with patch("check_kicad.cli_major", return_value=10):
                self.assertEqual(find_cli(cli, 10), cli.resolve())

    def test_manifest_uses_the_shared_exact_cli_resolver(self) -> None:
        self.assertIs(manifest_cli, find_cli)

    def test_detects_an_invalid_root_level_pcb_uuid(self) -> None:
        fixture = Path(__file__).parent / "fixtures" / "pcb" / "root-uuid.kicad_pcb"
        self.assertTrue(board_has_root_uuid(fixture))


if __name__ == "__main__":
    unittest.main()
