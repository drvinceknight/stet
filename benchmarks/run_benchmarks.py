"""Benchmark the overhead of stet across backends and store sizes."""

from __future__ import annotations

import csv
import statistics
import tempfile
import time
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import stet

from stet.backends._csv import CsvBackend
from stet.backends._json import JsonBackend
from stet.backends._sqlite import SqliteBackend

try:
    from stet.backends._parquet import ParquetBackend

    HAS_PARQUET = True
except ImportError:
    HAS_PARQUET = False

BACKENDS = {
    "CSV": CsvBackend,
    "JSON": JsonBackend,
    "SQLite": SqliteBackend,
}
if HAS_PARQUET:
    BACKENDS["Parquet"] = ParquetBackend  # type: ignore[assignment]

EXTENSIONS = {
    "CSV": "csv",
    "JSON": "json",
    "SQLite": "sqlite",
    "Parquet": "parquet",
}

N_REPEATS = 20
STORE_SIZES = [
    0,
    10,
    100,
    500,
    1000,
    2000,
    5000,
    10000,
    25000,
    50000,
    100000,
    150000,
    200000,
]

RESULTS_PATH = Path(__file__).parent / "benchmark_results.csv"
STET_STORE = Path(__file__).parent / "store.csv"


def measure(fn, n: int = N_REPEATS) -> tuple[float, float]:
    """Return (mean_ms, stdev_ms) over n repetitions."""
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        times.append((time.perf_counter() - t0) * 1000)
    return statistics.mean(times), statistics.stdev(times)


def bench_all(
    backend_cls, ext: str, n_existing: int
) -> tuple[float, float, float, float]:
    """Run all measurements for a backend and store size in a single pass.

    Returns (has_hit_ms, has_miss_ms, record_ms, file_size_kb).
    """
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / f"store.{ext}"
        b = backend_cls(path)
        for i in range(n_existing):
            b.record({"x": i, "y": i * 2})

        file_size_kb = path.stat().st_size / 1024 if path.exists() else 0.0

        absent = {"x": 999_999, "y": 999_999}
        has_miss_mean, _ = measure(lambda: b.has(absent))

        if n_existing == 0:
            b.record({"x": 0, "y": 0})
        target = {"x": max(n_existing, 1) - 1, "y": (max(n_existing, 1) - 1) * 2}
        has_hit_mean, _ = measure(lambda: b.has(target))

        counter = [max(n_existing, 1)]

        def fn() -> None:
            b.record({"x": counter[0], "y": counter[0] * 2})
            counter[0] += 1

        rec_mean, _ = measure(fn)
        return has_hit_mean, has_miss_mean, rec_mean, file_size_kb


@stet.once(store=str(STET_STORE), key=["name", "n"])
def run_and_record(name: str, n: int) -> None:
    cls = BACKENDS[name]
    ext = EXTENSIONS[name]
    hit, miss, rec, kb = bench_all(cls, ext, n)
    with open(RESULTS_PATH, "a", newline="") as f:
        csv.writer(f).writerow([name, n, hit, miss, rec, kb])
    print(
        f"  n={n:6d}  has_hit={hit:.2f}ms"
        f"  has_miss={miss:.2f}ms  record={rec:.2f}ms  size={kb:.1f}KB"
    )


def run_benchmarks() -> dict[str, dict[str, list]]:
    for name in BACKENDS:
        print(f"\n{name}")
        for n in STORE_SIZES:
            run_and_record(name=name, n=n)

    rows: dict[tuple[str, int], list] = {}
    with open(RESULTS_PATH, newline="") as f:
        for name, n, hit, miss, rec, kb in csv.reader(f):
            rows[(name, int(n))] = [float(hit), float(miss), float(rec), float(kb)]

    results: dict[str, dict[str, list]] = {
        name: {
            "sizes": [],
            "has_hit": [],
            "has_miss": [],
            "record": [],
            "file_size_kb": [],
        }
        for name in BACKENDS
    }
    for name in BACKENDS:
        for n in STORE_SIZES:
            hit, miss, rec, kb = rows[(name, n)]
            results[name]["sizes"].append(n)
            results[name]["has_hit"].append(hit)
            results[name]["has_miss"].append(miss)
            results[name]["record"].append(rec)
            results[name]["file_size_kb"].append(kb)

    return results


def plot_results(results: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    colors = {
        "CSV": "#1f77b4",
        "JSON": "#ff7f0e",
        "SQLite": "#2ca02c",
        "Parquet": "#d62728",
    }

    # --- Plot 1: has() scaling (hit and miss) ---
    fig, ax = plt.subplots(figsize=(7, 4))
    for name, data in results.items():
        ax.plot(
            data["sizes"],
            data["has_hit"],
            marker="o",
            label=f"{name} (hit)",
            color=colors[name],
        )
        ax.plot(
            data["sizes"],
            data["has_miss"],
            marker="s",
            linestyle="--",
            label=f"{name} (miss)",
            color=colors[name],
            alpha=0.6,
        )
    ax.set_xlabel("Records in store")
    ax.set_ylabel("Time (ms)")
    ax.set_title("has() overhead by store size (solid=hit, dashed=miss)")
    ax.legend(fontsize="small", ncol=2)
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "skip_overhead.png", dpi=150)
    plt.close(fig)
    print(f"\nSaved: {out_dir / 'skip_overhead.png'}")

    # --- Plot 2: record() scaling ---
    fig, ax = plt.subplots(figsize=(7, 4))
    for name, data in results.items():
        ax.plot(
            data["sizes"], data["record"], marker="o", label=name, color=colors[name]
        )
    ax.set_xlabel("Records in store")
    ax.set_ylabel("Time (ms)")
    ax.set_title("Record overhead by store size")
    ax.legend()
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "record_overhead.png", dpi=150)
    plt.close(fig)
    print(f"Saved: {out_dir / 'record_overhead.png'}")


def plot_file_sizes(results: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    colors = {
        "CSV": "#1f77b4",
        "JSON": "#ff7f0e",
        "SQLite": "#2ca02c",
        "Parquet": "#d62728",
    }

    x_extrap = max(STORE_SIZES) * 5
    x_fit = np.linspace(0, x_extrap, 500)

    fig, ax = plt.subplots(figsize=(8, 5))
    model_lines = ["f(n) = a\u00b7n + b  [KB]", ""]
    for name, data in results.items():
        sizes = np.array(data["sizes"], dtype=float)
        file_sizes = np.array(data["file_size_kb"], dtype=float)

        ax.plot(sizes, file_sizes, marker="o", color=colors[name], label=name)

        a, b = np.polyfit(sizes, file_sizes, 1)
        ax.plot(x_fit, a * x_fit + b, "--", color=colors[name], alpha=0.5)

        sign = "+" if b >= 0 else "-"
        model_lines.append(f"{name:<8s}  a={a:.5f}  b={sign}{abs(b):.1f}")

    ax.axvline(
        max(STORE_SIZES),
        color="gray",
        linestyle=":",
        alpha=0.5,
        label=f"benchmark limit ({max(STORE_SIZES):,})",
    )
    ax.text(
        0.02,
        0.98,
        "\n".join(model_lines),
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=8,
        fontfamily="monospace",
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "alpha": 0.85},
    )
    ax.set_xlabel("Records in store")
    ax.set_ylabel("File size (KB)")
    ax.set_title("Store file size by record count (dashed = linear extrapolation)")
    ax.legend(loc="upper right", fontsize="small")
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "file_size.png", dpi=150)
    plt.close(fig)
    print(f"Saved: {out_dir / 'file_size.png'}")


if __name__ == "__main__":
    out_dir = Path(__file__).parent.parent / "docs" / "img"
    results = run_benchmarks()
    plot_results(results, out_dir)
    plot_file_sizes(results, out_dir)
    print("\nDone.")
