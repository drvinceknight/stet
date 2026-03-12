# Resume a Sweep

Whether your script stopped because of a crash, a time limit, or a deliberate interruption, simply restart it. `stet` will skip every combination already in the store and pick up where it left off:

```python
for alpha in alphas:
    for seed in seeds:
        run_experiment(alpha=alpha, seed=seed)  # skips completed runs automatically
```

This also works when you extend a sweep — for example, adding new values to `alphas` or `seeds` after an initial run. Completed combinations are skipped; new ones run as normal.

To minimise the risk of output and store getting out of sync, write output *after* the decorated function returns rather than inside it:

```python
@stet.once(key=['alpha', 'seed'])
def run_experiment(alpha, seed):
    return compute_result(alpha, seed)

for alpha in alphas:
    for seed in seeds:
        result = run_experiment(alpha=alpha, seed=seed)
        if result is not None:   # None means the run was skipped
            write_output(result)
```

See [How stet Works](../explanation/how-once-works.md) for a fuller discussion of the two-file design.
