# Choose Key Parameters

## Use all parameters (the default)

Omit `key=` to use every parameter as part of the key:

```python
@stet.once
def run_experiment(alpha, seed, n_iter=1000):
    ...
```

Use this when every parameter genuinely changes the result.

## Specify key parameters explicitly

Use `key=` to exclude parameters that don't define the experiment — for example, computational settings like `n_iter`, `batch_size`, or `verbose`:

```python
@stet.once(key=['alpha', 'seed'])
def run_experiment(alpha, seed, n_iter=1000):
    ...
```

Now only `alpha` and `seed` determine whether a run is skipped, regardless of `n_iter`.

## Exclude parameters with default values from the key

If a parameter has a default value and you call the function both with and without it, the two calls will be treated as different runs unless you exclude it from the key:

```python
# without key=, these are different runs:
run_experiment(alpha=0.1, seed=1)              # n_iter=1000 (default)
run_experiment(alpha=0.1, seed=1, n_iter=500)  # n_iter=500

# with key=['alpha', 'seed'], both are the same run:
run_experiment(alpha=0.1, seed=1)
run_experiment(alpha=0.1, seed=1, n_iter=500)  # skipped
```

See [How stet Works](../explanation/how-once-works.md) for a fuller discussion of how parameter identity is determined.
