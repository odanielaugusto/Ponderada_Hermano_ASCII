import json
import time
from pathlib import Path

import pytest

from ascii_art import render_text

PROFILE_PATH = Path(__file__).resolve().parents[1] / "experiment" / "profile.json"
PROFILE = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def test_profile_has_required_fields() -> None:
    assert {"scenario", "extra_cases", "slow_ms", "force_failure"} <= set(PROFILE)


def test_controlled_failure_switch_is_off() -> None:
    assert not PROFILE["force_failure"], f"Controlled failure for {PROFILE['scenario']}"


def test_optional_slow_scenario() -> None:
    slow_seconds = int(PROFILE["slow_ms"]) / 1000
    if slow_seconds:
        time.sleep(slow_seconds)

    assert render_text(PROFILE["scenario"])


@pytest.mark.parametrize("case_index", range(max(1, int(PROFILE["extra_cases"]))))
def test_generated_cases_from_profile(case_index: int) -> None:
    art = render_text(f"{PROFILE['scenario']} {case_index}")

    assert len(art.splitlines()) == 5
