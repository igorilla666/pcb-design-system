from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


class SnapshotProjectTests(unittest.TestCase):
    def test_snapshot_requires_clean_source_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "docs").mkdir()
            (root / "docs" / "PROJECT_LOG.md").write_text("# Log\n", encoding="utf-8")
            (root / "board.kicad_pro").write_text("{}\n", encoding="utf-8")
            (root / ".gitignore").write_text("build/\n", encoding="utf-8")
            git(root, "init")
            git(root, "config", "user.name", "Test")
            git(root, "config", "user.email", "test@example.invalid")
            git(root, "add", ".")
            git(root, "commit", "-m", "initial")

            clean = subprocess.run(
                [sys.executable, str(SCRIPTS / "snapshot_project.py"), str(root), "--label", "clean"],
                check=False, capture_output=True, text=True,
            )
            self.assertEqual(clean.returncode, 0, clean.stderr)
            self.assertIn("Created snapshot", clean.stdout)

            (root / "uncommitted.txt").write_text("dirty\n", encoding="utf-8")
            dirty = subprocess.run(
                [sys.executable, str(SCRIPTS / "snapshot_project.py"), str(root)],
                check=False, capture_output=True, text=True,
            )
            self.assertNotEqual(dirty.returncode, 0)
            self.assertIn("worktree is dirty", dirty.stderr)

    def test_snapshot_excludes_ad_hoc_build_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "docs").mkdir()
            (root / "docs" / "PROJECT_LOG.md").write_text("# Log\n", encoding="utf-8")
            (root / "board.kicad_pro").write_text("{}\n", encoding="utf-8")
            (root / ".gitignore").write_text("build/\n", encoding="utf-8")
            git(root, "init")
            git(root, "config", "user.name", "Test")
            git(root, "config", "user.email", "test@example.invalid")
            git(root, "add", ".")
            git(root, "commit", "-m", "initial")

            build = root / "build" / "pcb-design-check"
            build.mkdir(parents=True)
            (build / "board-erc.rpt").write_text("gate\n", encoding="utf-8")
            (build / "debug_probe-erc.rpt").write_text("scratch\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "snapshot_project.py"), str(root), "--label", "curated"],
                check=False, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            snapshot = next((root / "docs" / "validation").glob("*-curated"))
            evidence = snapshot / "evidence"
            self.assertTrue((evidence / "board-erc.rpt").is_file())
            self.assertFalse((evidence / "debug_probe-erc.rpt").exists())


if __name__ == "__main__":
    unittest.main()
