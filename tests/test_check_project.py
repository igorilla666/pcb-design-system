"""Regression tests for the Git repository gate in check_project.py."""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_project.py"
SPEC = importlib.util.spec_from_file_location("check_project", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GitRepositoryGateTests(unittest.TestCase):
    def test_empty_dot_git_directory_is_not_a_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            self.assertFalse(MODULE.is_valid_git_repository(root))

    def test_initialized_repository_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            self.assertTrue(MODULE.is_valid_git_repository(root))


if __name__ == "__main__":
    unittest.main()
