import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.resolve()
HARNESS_SCRIPT = REPO_ROOT / "harness" / "run_all.py"
CASES_DIR = REPO_ROOT / "harness" / "cases"


class TestHarnessLoadsCases:
    def test_harness_script_exists(self):
        assert HARNESS_SCRIPT.exists(), f"Harness script not found: {HARNESS_SCRIPT}"

    def test_cases_directory_exists(self):
        assert CASES_DIR.exists(), f"Cases directory not found: {CASES_DIR}"

    def test_at_least_six_cases_exist(self):
        cases = list(CASES_DIR.glob("*.json"))
        assert len(cases) >= 6, f"Expected at least 6 cases, found {len(cases)}"

    def test_all_cases_are_valid_json(self):
        for path in CASES_DIR.glob("*.json"):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert "case_name" in data, f"{path.name} missing case_name"
            assert "input" in data, f"{path.name} missing input"
            assert "expected_decision" in data, f"{path.name} missing expected_decision"


class TestHarnessRuns:
    def test_all_committed_cases_pass(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT)
        result = subprocess.run(
            [sys.executable, str(HARNESS_SCRIPT)],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, (
            f"Harness failed with code {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "All cases PASSED" in result.stdout

    def test_failing_case_produces_understandable_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a deliberately failing case
            bad_case = {
                "case_name": "deliberately_failing",
                "description": "This case should fail",
                "input": "user_001_good.jpg",
                "expected_decision": "deny",
                "expected_reason": "user_not_found",
            }
            bad_path = Path(tmpdir) / "bad_case.json"
            with open(bad_path, "w", encoding="utf-8") as f:
                json.dump(bad_case, f)

            # Run harness with only the bad case
            env = os.environ.copy()
            env["PYTHONPATH"] = str(REPO_ROOT)

            # Monkey-patch the harness to use tmpdir
            harness_code = HARNESS_SCRIPT.read_text(encoding="utf-8")
            harness_code = harness_code.replace(
                'CASES_DIR = Path(__file__).parent / "cases"',
                f'CASES_DIR = Path(r"{tmpdir}")',
            )

            tmp_harness = Path(tmpdir) / "run_all.py"
            tmp_harness.write_text(harness_code, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(tmp_harness)],
                capture_output=True,
                text=True,
                env=env,
                cwd=str(REPO_ROOT),
            )

            assert result.returncode != 0, "Expected harness to fail with bad case"
            assert "FAIL" in result.stdout, "Expected FAIL in output"
            assert "deliberately_failing" in result.stdout
            assert "decision mismatch" in result.stdout

    def test_cli_exits_zero_when_all_pass(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT)
        result = subprocess.run(
            [sys.executable, str(HARNESS_SCRIPT)],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0
