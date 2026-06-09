from __future__ import annotations

import argparse
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write CI metadata generated during a workflow run."
    )
    parser.add_argument("--junit", required=True, type=Path)
    parser.add_argument("--profile", default=Path("experiment/profile.json"), type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = {
        "run_id": os.getenv("GITHUB_RUN_ID", ""),
        "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT", ""),
        "workflow": os.getenv("GITHUB_WORKFLOW", ""),
        "commit_sha": os.getenv("GITHUB_SHA", git_value("rev-parse", "HEAD")),
        "commit_message": git_value("log", "-1", "--pretty=%s"),
        "timestamp": datetime.now(UTC).isoformat(),
        "profile": read_json(args.profile),
        "tests": read_junit(args.junit),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return 0


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_junit(path: Path) -> dict[str, float | int]:
    if not path.exists():
        return {
            "count": 0,
            "failures": 0,
            "errors": 0,
            "skipped": 0,
            "duration": 0.0,
            "average": 0.0,
        }

    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    total = sum(int(suite.attrib.get("tests", 0)) for suite in suites)
    failures = sum(int(suite.attrib.get("failures", 0)) for suite in suites)
    errors = sum(int(suite.attrib.get("errors", 0)) for suite in suites)
    skipped = sum(int(suite.attrib.get("skipped", 0)) for suite in suites)
    count = total - skipped
    duration = sum(float(suite.attrib.get("time", 0.0)) for suite in suites)
    average = duration / count if count else 0.0

    return {
        "count": count,
        "failures": failures + errors,
        "errors": errors,
        "skipped": skipped,
        "duration": round(duration, 3),
        "average": round(average, 3),
    }


def git_value(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


if __name__ == "__main__":
    raise SystemExit(main())
