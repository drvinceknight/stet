# Use with Multiprocessing

`stet` uses file-level locking via `filelock`, so it is safe to use with
`multiprocessing` or `joblib`.

## With `multiprocessing`

```python
import stet
from multiprocessing import Pool


@stet.once(store="results.sqlite", key=["alpha", "seed"])
def run_experiment(alpha, seed):
    # expensive computation
    pass


params = [(alpha, seed) for alpha in [0.1, 0.5, 1.0] for seed in range(10)]

with Pool(processes=4) as pool:
    pool.starmap(run_experiment, params)
```

Each worker acquires the file lock before reading or writing, so records are never
corrupted.

## With `joblib`

```python
from joblib import Parallel, delayed
import stet


@stet.once(store="_stet_store.csv", key=["x"])
def run(x):
    pass


Parallel(n_jobs=4)(delayed(run)(x=i) for i in range(100))
```

## Silence skip messages

By default `stet` prints a line each time it skips a completed run. When several
workers print at once these lines interleave and the output becomes hard to read. We
turn them off with `verbose=False`:

```python
@stet.once(store="results.sqlite", key=["alpha", "seed"], verbose=False)
def run_experiment(alpha, seed): ...
```

We can then check progress with `stet.status` once the workers have finished.

## Recommended backend for parallel workloads

SQLite is recommended for parallel workloads; it has better concurrent write performance
than CSV or JSON. Use:

```python
@stet.once(store="results.sqlite", key=["alpha", "seed"])
def run_experiment(alpha, seed): ...
```
