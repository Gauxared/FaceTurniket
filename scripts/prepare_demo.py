from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure repo root is importable when running the script directly.
repo_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(repo_root))

from src.demo.runner import load_runner_from_path, save_demo_report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare diploma presentation demo")
    parser.add_argument(
        "--config",
        default="demo/local/config.json",
        help="Path to local demo config JSON",
    )
    parser.add_argument(
        "--report",
        default="reports/demo_report.json",
        help="Path to output demo report JSON",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        raise SystemExit(
            f"Demo config not found: {config_path}. Create it from demo/config.example.json"
        )

    runner = load_runner_from_path(config_path)
    report = runner.run()
    save_demo_report(report, args.report)

    def _decision_text(section):
        if not section:
            return "skipped"
        if section.get("skipped"):
            return f"skipped ({section.get('reason', 'unknown')})"
        decision = section.get("decision", {})
        turnstile = section.get("turnstile_command", {})
        return f"{decision.get('decision', 'unknown')}/{turnstile.get('command', 'unknown')}"

    print("Demo preparation passed")
    print(f"Allowed photo: {_decision_text(report.get('positive_photo'))}")
    print(f"Unknown photo: {_decision_text(report.get('unknown_photo'))}")
    print(f"Low quality photo: {_decision_text(report.get('low_quality_photo'))}")
    print(f"Video: {_decision_text(report.get('video_result'))}")
    print(f"Report: {Path(args.report)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
