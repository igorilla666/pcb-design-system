from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SCRIPT = SCRIPTS / "check_tool_policy.py"


class ToolPolicyTests(unittest.TestCase):
    def make_project(self, root: Path, *, status: str = "approved", valid_hash: bool = True) -> None:
        tool = root / "tools" / "pcb_design" / "example.py"
        tool.parent.mkdir(parents=True)
        tool.write_text("print('ok')\n", encoding="utf-8")
        digest = hashlib.sha256(tool.read_bytes()).hexdigest() if valid_hash else "bad"
        docs = root / "docs"
        docs.mkdir()
        (docs / "tooling-manifest.json").write_text(json.dumps({"tools": [{
            "path": "tools/pcb_design/example.py", "purpose": "test", "status": status,
            "sha256": digest, "review_evidence": "test review",
        }]}), encoding="utf-8")

    def run_policy(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(SCRIPT), str(root)], check=False, capture_output=True, text=True)

    def test_approved_hashed_tool_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_project(root)
            result = self.run_policy(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_changed_or_unapproved_tool_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_project(root, valid_hash=False)
            result = self.run_policy(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hash differs", result.stdout)
