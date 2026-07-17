#!/usr/bin/env python3
"""Run structured framework test suites and write a concise local report."""

from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
SUITES = {
    "fast": ["test_check_project.py", "test_dependency_policy.py", "test_electrical_manifest.py", "test_kicad_toolchain.py", "test_tool_policy.py"],
    "template": ["test_generator_contract_templates.py", "test_pcb_constraints.py", "test_schematic_layout_manifest.py", "test_schematic_layout_plan.py", "test_snapshot_project.py"],
    "fixtures": ["test_regression_fixtures.py"],
    "kicad": ["test_kicad_integration.py"],
}


def load_suite(names: list[str]) -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in names:
        suite.addTests(loader.discover(str(TESTS), pattern=name))
    return suite


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=[*SUITES, "all"], action="append", help="May be repeated; defaults to all")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "build" / "framework-test")
    args = parser.parse_args()
    selected = args.suite or ["all"]
    names = list(SUITES) if "all" in selected else selected
    files = [item for name in names for item in SUITES[name]]
    result = unittest.TextTestRunner(verbosity=2).run(load_suite(files))
    report_dir = args.report_dir.expanduser().resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    report = report_dir / "summary.txt"
    report.write_text(
        "Framework test summary\n"
        f"Suites: {', '.join(names)}\n"
        f"Run: {result.testsRun}\n"
        f"Failures: {len(result.failures)}\n"
        f"Errors: {len(result.errors)}\n"
        f"Skipped: {len(result.skipped)}\n"
        f"Status: {'PASS' if result.wasSuccessful() else 'FAIL'}\n",
        encoding="utf-8",
    )
    print(f"Framework test report: {report}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
