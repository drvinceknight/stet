# Getting Started

In this tutorial, you'll install `stet`, decorate a simple function, and see the skip behaviour in action.

## Install

```
$ uv add stet
```

or

```
$ python -m pip install stet
```

## Decorate your function

```python
import stet

@stet.once
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
[stet] Skipping run_experiment(alpha=0.1, seed=1)
[stet] Skipping run_experiment(alpha=0.1, seed=2)
[stet] Skipping run_experiment(alpha=0.5, seed=1)
```

On the second run, every experiment is skipped because the `(alpha, seed)` combinations are already in `_stet_store.csv` (the default store, created automatically in your working directory). This works whether the script was stopped by a crash, a time limit, or deliberately.

## Check progress

```python
import stet
stet.status()
```

```
[stet] Store: _stet_store.csv  ← created automatically in your working directory
[stet] 3 completed experiments recorded
[stet] Last run: 2024-11-03T14:22:01
[stet] Key columns: alpha, seed
```

Congratulations — you've seen the core feature of `stet` in action!
