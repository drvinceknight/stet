"""Benchmark the overhead of stet across backends and store sizes."""

from __future__ import annotations

import statistics
import tempfile
import time
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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

N_REPEATS = 20  # repetitions per measurement
STORE_SIZES = [0, 10, 100, 500, 1000, 2000, 5000, 10000]


def measure(fn, n: int = N_REPEATS) -> tuple[float, float]:
    """Return (mean_ms, stdev_ms) over n repetitions."""
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        times.append((time.perf_counter() - t0) * 1000)
    return statistics.mean(times), statistics.stdev(times)


def bench_record(backend_cls, ext: str, n_existing: int) -> tuple[float, float]:
    """Time a single record() call with n_existing records already present."""
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / f"store.{ext}"
        b = backend_cls(path)
        for i in range(n_existing):
            b.record({"x": i, "y": i * 2})

        counter = [n_existing]

        def fn() -> None:
            b.record({"x": counter[0], "y": counter[0] * 2})
            counter[0] += 1

        return measure(fn)


def bench_has_hit(backend_cls, ext: str, n_existing: int) -> tuple[float, float]:
    """Time a has() call that returns True (skip path) with n_existing records."""
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / f"store.{ext}"
        b = backend_cls(path)
        for i in range(n_existing):
            b.record({"x": i, "y": i * 2})
        # target: last record inserted
        target = {"x": n_existing - 1, "y": (n_existing - 1) * 2}
        return measure(lambda: b.has(target))


def bench_has_miss(backend_cls, ext: str, n_existing: int) -> tuple[float, float]:
    """Time a has() call that returns False (run path) with n_existing records."""
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / f"store.{ext}"
        b = backend_cls(path)
        for i in range(n_existing):
            b.record({"x": i, "y": i * 2})
        absent = {"x": 999_999, "y": 999_999}
        return measure(lambda: b.has(absent))


def run_scaling_benchmark() -> dict[str, dict[str, list]]:
    """
    For each backend, measure has() (hit and miss) and record() time
    as store size grows.
    """
    results: dict[str, dict[str, list]] = {
        name: {"sizes": [], "has_hit": [], "has_miss": [], "record": []}
        for name in BACKENDS
    }

    for name, cls in BACKENDS.items():
        ext = EXTENSIONS[name]
        print(f"\n{name}")
        for n in STORE_SIZES:
            if n == 0 and name != "SQLite":
                # has() on empty store is trivial; use 1 as minimum for has_hit
                hit_mean, _ = bench_has_hit(cls, ext, max(n, 1))
            else:
                hit_mean, _ = bench_has_hit(cls, ext, max(n, 1))
            miss_mean, _ = bench_has_miss(cls, ext, n)
            rec_mean, _ = bench_record(cls, ext, n)
            results[name]["sizes"].append(n)
            results[name]["has_hit"].append(hit_mean)
            results[name]["has_miss"].append(miss_mean)
            results[name]["record"].append(rec_mean)
            print(
                f"  n={n:5d}  has_hit={hit_mean:.2f}ms"
                f"  has_miss={miss_mean:.2f}ms  record={rec_mean:.2f}ms"
            )

    return results


def plot_results(results: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    colors = {
        "CSV": "#1f77b4",
        "JSON": "#ff7f0e",
        "SQLite": "#2ca02c",
        "Parquet": "#d62728",
    }

    # --- Plot 1: has() scaling (skip path) ---
    fig, ax = plt.subplots(figsize=(7, 4))
    for name, data in results.items():
        ax.plot(
            data["sizes"], data["has_hit"], marker="o", label=name, color=colors[name]
        )
    ax.set_xlabel("Records in store")
    ax.set_ylabel("Time (ms)")
    ax.set_title("Skip check overhead by store size")
    ax.legend()
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


if __name__ == "__main__":
    print("Running benchmarks...")
    results = run_scaling_benchmark()
    out_dir = Path(__file__).parent.parent / "docs" / "img"
    plot_results(results, out_dir)
    print("\nDone.")
