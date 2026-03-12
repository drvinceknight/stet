# Getting Started

In this tutorial, you'll install `once`, decorate a simple function, and see the skip behaviour in action.

## Install

```
$ uv add once
```

or

```
$ python -m pip install once
```

## Decorate your function

```python
import once

@once.once
def run_experiment(alpha, seed, n_iter=500):
    print(f"  Running alpha={alpha}, seed={seed}")
    # simulate work
    import time
    time.sleep(0.1)
```

## Run it twice

```python
params = [(0.1, 1), (0.1, 2), (0.5, 1)]

print("=== First run ===")
for alpha, seed in params:
    run_experiment(alpha=alpha, seed=seed)

print("\n=== Second run ===")
for alpha, seed in params:
    run_experiment(alpha=alpha, seed=seed)
```

**Output:**

```
=== First run ===
  Running alpha=0.1, seed=1
  Running alpha=0.1, seed=2
  Running alpha=0.5, seed=1

=== Second run ===
[once] Skipping run_experiment(alpha=0.1, seed=1)
[once] Skipping run_experiment(alpha=0.1, seed=2)
[once] Skipping run_experiment(alpha=0.5, seed=1)
```

On the second run, every experiment is skipped because the `(alpha, seed)` combinations are already in `_once_store.csv` (the default store, created automatically in your working directory). This works whether the script was stopped by a crash, a time limit, or deliberately.

## Check progress

```python
import once
once.status()
```

```
[once] Store: _once_store.csv  ← created automatically in your working directory
[once] 3 completed experiments recorded
[once] Last run: 2024-11-03T14:22:01
[once] Key columns: alpha, seed
```

Congratulations — you've seen the core feature of `once` in action!
