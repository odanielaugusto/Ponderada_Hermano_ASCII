from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate charts from pipeline metrics CSV.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    data = pd.read_csv(args.input)
    if data.empty:
        raise SystemExit("Metrics file is empty.")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    run_data = (
        data.sort_values(["timestamp", "run_id"])
        .drop_duplicates("run_id")
        .reset_index(drop=True)
    )
    run_data["execution"] = range(1, len(run_data) + 1)

    plot_total_duration(run_data, args.out_dir / "tempo_total_por_execucao.png")
    plot_job_duration(data, args.out_dir / "tempo_por_job.png")
    plot_status_rate(run_data, args.out_dir / "taxa_sucesso_falha.png")
    plot_tests_vs_duration(run_data, args.out_dir / "testes_vs_duracao.png")

    print(f"Charts written to {args.out_dir}")
    return 0


def plot_total_duration(run_data: pd.DataFrame, out: Path) -> None:
    colors = run_data["status"].map({"success": "#2e7d32", "failure": "#c62828"}).fillna("#455a64")
    plt.figure(figsize=(10, 5))
    plt.bar(run_data["execution"], run_data["workflow_duration"], color=colors)
    plt.xlabel("Execucao")
    plt.ylabel("Duracao total (s)")
    plt.title("Tempo total do pipeline por execucao")
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()


def plot_job_duration(data: pd.DataFrame, out: Path) -> None:
    job_data = data.drop_duplicates(["run_id", "job_name"])
    pivot = job_data.pivot_table(
        index="run_id",
        columns="job_name",
        values="job_duration",
        aggfunc="first",
    )
    pivot.plot(kind="bar", figsize=(11, 5))
    plt.xlabel("Run ID")
    plt.ylabel("Duracao do job (s)")
    plt.title("Tempo por job")
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()


def plot_status_rate(run_data: pd.DataFrame, out: Path) -> None:
    counts = run_data["status"].value_counts()
    colors = ["#2e7d32" if status == "success" else "#c62828" for status in counts.index]
    plt.figure(figsize=(7, 5))
    counts.plot(kind="bar", color=colors)
    plt.xlabel("Status")
    plt.ylabel("Quantidade")
    plt.title("Taxa de sucesso e falha")
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()


def plot_tests_vs_duration(run_data: pd.DataFrame, out: Path) -> None:
    plt.figure(figsize=(8, 5))
    plt.scatter(run_data["test_count"], run_data["workflow_duration"], color="#1565c0", s=80)
    for _, row in run_data.iterrows():
        plt.annotate(str(row["execution"]), (row["test_count"], row["workflow_duration"]))
    plt.xlabel("Quantidade de testes")
    plt.ylabel("Duracao total (s)")
    plt.title("Relacao entre quantidade de testes e duracao")
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()


if __name__ == "__main__":
    raise SystemExit(main())
