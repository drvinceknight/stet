# Import Existing Results into a Store

If you have already run experiments and have results in a data file, you can pre-populate a `once` store so that those runs are skipped when you restart.

## The situation

You have a file such as `my_results.csv` with columns for your parameters and results:

```
alpha,seed,mse
0.1,0,0.42
0.1,1,0.38
0.2,0,0.51
```

You now want to decorate your experiment function with `@once` and re-run your full sweep, but without repeating the work already done.

## Step 1: Pre-populate the store

Use the backend directly to record each parameter combination present in your existing data:

```python
import pandas as pd
from once.backends import get_backend
from pathlib import Path

df = pd.read_csv("my_results.csv")

backend = get_backend(Path("_once_store.csv"))
for _, row in df.iterrows():
    backend.record({"alpha": row["alpha"], "seed": row["seed"]})
```

Only include the parameter columns — not result columns like `mse`. The store tracks which parameter combinations have been run, not what they produced.

## Step 2: Decorate and re-run

```python
import once

@once.once(key=["alpha", "seed"])
def run_experiment(alpha, seed):
    ...

for alpha in [0.1, 0.2, 0.3]:
    for seed in range(5):
        run_experiment(alpha, seed)
```

Combinations already in the store are skipped; only the missing ones execute.

## Matching parameter names and values

The parameter names used in `backend.record()` must match the names `once` extracts from your function — which are the argument names unless you override them with `key=`. Values are stored as strings internally, so `0.1` and `"0.1"` are treated the same.

You can verify the store looks correct before re-running:

```python
import once

once.status()
```

See [Inspect a Store](inspect-and-reset-a-store.md) for more detail on reading store contents.
