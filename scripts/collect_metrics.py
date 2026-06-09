from __future__ import annotations

import argparse
import csv
import io
import json
import os
import subprocess
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

CSV_COLUMNS = [
    "run_id",
    "run_number",
    "commit_sha",
    "commit_message",
    "status",
    "workflow_duration",
    "job_name",
    "job_duration",
    "step_name",
    "step_duration",
    "test_count",
    "test_failures",
    "test_average_time",
    "timestamp",
    "scenario",
    "html_url",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect GitHub Actions metrics into CSV.")
    parser.add_argument("--repo", required=True, help="Repository in owner/name format.")
    parser.add_argument("--workflow", default="ci.yml", help="Workflow file name or workflow id.")
    parser.add_argument(
        "--run-id",
        action="append",
        help="Specific run id. Can be used more than once.",
    )
    parser.add_argument("--limit", default=30, type=int, help="Number of recent runs to inspect.")
    parser.add_argument("--out", required=True, type=Path, help="Output CSV path.")
    parser.add_argument(
        "--token",
        default=os.getenv("GITHUB_TOKEN"),
        help="GitHub token, optional.",
    )
    args = parser.parse_args()

    client = GitHubClient(args.token)
    runs = get_runs(client, args.repo, args.workflow, args.run_id, args.limit)
    rows: list[dict[str, Any]] = []

    for run in runs:
        metadata = get_artifact_metadata(client, args.repo, run["id"]) if client.token else {}
        jobs = client.get_paginated(f"/repos/{args.repo}/actions/runs/{run['id']}/jobs")
        profile = metadata.get("profile") or get_profile_from_git(
            run.get("head_sha", "")
        ) or get_profile_from_commit(
            client,
            args.repo,
            run.get("head_sha", ""),
        )
        test_data = metadata.get("tests") or infer_test_data(profile, jobs)
        workflow_duration = seconds_between(run.get("run_started_at"), run.get("updated_at"))

        for job in jobs:
            job_duration = seconds_between(job.get("started_at"), job.get("completed_at"))
            steps = job.get("steps") or [{"name": "", "started_at": "", "completed_at": ""}]
            for step in steps:
                rows.append(
                    {
                        "run_id": run["id"],
                        "run_number": run.get("run_number", ""),
                        "commit_sha": run.get("head_sha", ""),
                        "commit_message": first_line(
                            (run.get("head_commit") or {}).get("message", "")
                        ),
                        "status": run.get("conclusion") or run.get("status", ""),
                        "workflow_duration": workflow_duration,
                        "job_name": job.get("name", ""),
                        "job_duration": job_duration,
                        "step_name": step.get("name", ""),
                        "step_duration": seconds_between(
                            step.get("started_at"), step.get("completed_at")
                        ),
                        "test_count": test_data.get("count", ""),
                        "test_failures": test_data.get("failures", ""),
                        "test_average_time": test_data.get("average", ""),
                        "timestamp": run.get("run_started_at", ""),
                        "scenario": profile.get("scenario", ""),
                        "html_url": run.get("html_url", ""),
                    }
                )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {args.out}")
    return 0


class GitHubClient:
    def __init__(self, token: str | None) -> None:
        self.token = token

    def get_json(self, path_or_url: str) -> Any:
        data = self.get_bytes(path_or_url)
        return json.loads(data.decode("utf-8"))

    def get_bytes(self, path_or_url: str) -> bytes:
        url = path_or_url
        if path_or_url.startswith("/"):
            url = f"https://api.github.com{path_or_url}"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "ascii-art-ci-metrics",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = Request(url, headers=headers)
        with urlopen(request, timeout=30) as response:
            return response.read()

    def get_paginated(self, path: str, *, per_page: int = 100) -> list[dict[str, Any]]:
        page = 1
        items: list[dict[str, Any]] = []
        while True:
            separator = "&" if "?" in path else "?"
            payload = self.get_json(f"{path}{separator}per_page={per_page}&page={page}")
            key = next(
                (name for name in ("workflow_runs", "jobs", "artifacts") if name in payload),
                None,
            )
            batch = payload[key] if key else payload
            if not batch:
                break
            items.extend(batch)
            if len(batch) < per_page:
                break
            page += 1
        return items


def get_runs(
    client: GitHubClient,
    repo: str,
    workflow: str,
    run_ids: list[str] | None,
    limit: int,
) -> list[dict[str, Any]]:
    if run_ids:
        return [client.get_json(f"/repos/{repo}/actions/runs/{run_id}") for run_id in run_ids]

    runs = client.get_paginated(f"/repos/{repo}/actions/workflows/{workflow}/runs")
    completed = [run for run in runs if run.get("status") == "completed"]
    return completed[:limit]


def get_artifact_metadata(client: GitHubClient, repo: str, run_id: int) -> dict[str, Any]:
    try:
        artifacts = client.get_paginated(f"/repos/{repo}/actions/runs/{run_id}/artifacts")
    except (HTTPError, URLError):
        return {}

    for artifact in artifacts:
        is_result_artifact = artifact.get("name", "").startswith("ascii-art-ci-results")
        if artifact.get("expired") or not is_result_artifact:
            continue
        try:
            archive = client.get_bytes(artifact["archive_download_url"])
            return read_metadata_from_zip(archive)
        except (HTTPError, URLError, KeyError, zipfile.BadZipFile):
            continue
    return {}


def get_profile_from_commit(client: GitHubClient, repo: str, commit_sha: str) -> dict[str, Any]:
    if not commit_sha:
        return {}
    url = f"https://raw.githubusercontent.com/{repo}/{commit_sha}/experiment/profile.json"
    try:
        return json.loads(client.get_bytes(url).decode("utf-8"))
    except (HTTPError, URLError, json.JSONDecodeError):
        return {}


def get_profile_from_git(commit_sha: str) -> dict[str, Any]:
    if not commit_sha:
        return {}
    try:
        raw = subprocess.check_output(
            ["git", "show", f"{commit_sha}:experiment/profile.json"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return json.loads(raw)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError):
        return {}


def infer_test_data(profile: dict[str, Any], jobs: list[dict[str, Any]]) -> dict[str, Any]:
    if not profile:
        return {}

    static_tests_outside_generated_case = 11
    generated_cases = max(1, int(profile.get("extra_cases", 0)))
    count = static_tests_outside_generated_case + generated_cases
    failures = 1 if profile.get("force_failure") else 0
    pytest_duration = get_step_duration(jobs, job_name="tests", step_name="Run Pytest")
    average = pytest_duration / count if count else 0.0

    return {
        "count": count,
        "failures": failures,
        "average": round(average, 3),
    }


def get_step_duration(jobs: list[dict[str, Any]], *, job_name: str, step_name: str) -> float:
    for job in jobs:
        if job.get("name") != job_name:
            continue
        for step in job.get("steps", []):
            if step.get("name") == step_name:
                return seconds_between(step.get("started_at"), step.get("completed_at"))
    return 0.0


def read_metadata_from_zip(archive: bytes) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as _:
        with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
            for name in zipped.namelist():
                if name.endswith("run-metadata.json"):
                    return json.loads(zipped.read(name).decode("utf-8"))
    return {}


def seconds_between(start: str | None, end: str | None) -> float:
    if not start or not end:
        return 0.0
    return round((parse_time(end) - parse_time(start)).total_seconds(), 3)


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def first_line(value: str) -> str:
    return value.splitlines()[0] if value else ""


if __name__ == "__main__":
    raise SystemExit(main())
