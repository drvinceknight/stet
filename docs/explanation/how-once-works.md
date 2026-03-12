# How stet Works

## Parameter-keyed tracking, not memoization

Traditional memoization (e.g. `functools.lru_cache`) stores the *return value* of a function so that repeated calls with the same inputs return the cached result. `stet` does something different: it tracks *which parameter combinations have been executed* and skips them on future calls — without storing return values at all.

This distinction matters for experiment scripts. Researchers typically write their own outputs (CSV rows, model files, database records). What they need is not cached results, but a durable record of which experiments have already run.

## How the decorator works

When you write:

```python
@stet.once(store='_stet_store.csv', key=['alpha', 'beta'])
def run_experiment(alpha, beta, n_steps):
    ...
```

`stet` wraps `run_experiment` so that each call:

1. Binds all arguments to their parameter names using `inspect.signature`.
2. Extracts only the `key` parameters (`alpha`, `beta`).
3. Checks the store: has this `(alpha, beta)` combination been recorded?
4. If yes: prints a skip message and returns `None`.
5. If no: calls the real function, then records the key parameters plus a timestamp.

## Why the store is separate from your data

A natural question is: why not write results directly into the store file, so there is only one file to manage?

The short answer is that experiment outputs are too varied for `stet` to own them. A single experiment might produce a row in a CSV, a trained model checkpoint, a plot, entries in a database, or all of the above. There is no single file format or schema that fits every case, and any attempt to impose one would either be too restrictive or too complex to be useful.

Keeping the store separate means `stet` only needs to solve the narrow problem it was designed for — *did this parameter combination run?* — and leaves the richer question of *what did it produce?* entirely to you. This also means your output files stay in whatever format your analysis tools already expect, with no `stet`-specific structure mixed in.

The practical consequence is two files: a `_stet_store.csv` (or `.sqlite`, `.json`, etc.) that `stet` manages, and your own output file that your script manages. If you want to check whether a particular run completed, use `stet.status()`; if you want to inspect the results, open your output file directly.

There is one failure mode worth being aware of: if your function crashes *after* writing output but *before* returning (so `stet` never records the run), the store and your output file will be out of sync. On restart `stet` will re-run that experiment. Whether that is a problem depends on your output — appending a duplicate row to a CSV is usually harmless; re-training an expensive model is not. If atomicity matters, the safest pattern is to return results from the function and write output *after* the call returns:

```python
@stet.once(store='_stet_store.csv', key=['alpha', 'seed'])
def run_experiment(alpha, seed):
    return expensive_computation(alpha, seed)

for alpha in alphas:
    for seed in seeds:
        result = run_experiment(alpha=alpha, seed=seed)
        if result is not None:   # None means the run was skipped
            write_output(result)
```

This way `stet` records the run only after the function has completed successfully, and you write output only after `stet` has recorded it.

## Backend selection

The backend is selected automatically from the file extension:

- `.csv` → `CsvBackend` (pandas)
- `.parquet` → `ParquetBackend` (pandas + pyarrow)
- `.sqlite` / `.db` → `SqliteBackend` (stdlib sqlite3)
- `.json` → `JsonBackend` (stdlib json)

All backends implement the same interface (`BaseBackend`), so they're interchangeable.

## File locking

`stet` uses `filelock` to acquire a file-level lock before every read or write. This ensures that concurrent processes (e.g. `multiprocessing`, `joblib`) cannot corrupt the store. The lock is released immediately after the operation.
