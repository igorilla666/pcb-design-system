from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SCRIPT = SCRIPTS / "check_dependency_policy.py"


POLICY = """# Dependency contract

- Status: acknowledged

## Allowed sources

1. Repository.

## Prohibited discovery

- No scanning.

## Dependency ledger

| ID | Type | Source and provenance | Version | License | SHA-256 | Promoted repository path | User approval |
| --- | --- | --- | --- | --- | --- | --- | --- |
| none | — | No external dependency promoted. | — | — | — | — | — |
"""


class DependencyPolicyTests(unittest.TestCase):
    def test_acknowledged_policy_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / "docs"
            docs.mkdir()
            (docs / "DEPENDENCIES.md").write_text(POLICY, encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(root)], check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pending_policy_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / "docs"
            docs.mkdir()
            (docs / "DEPENDENCIES.md").write_text(POLICY.replace("acknowledged", "pending", 1), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(root)], check=False, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("status must be acknowledged", result.stdout)


if __name__ == "__main__":
    unittest.main()
