# Decorate a Function with `once`

## Zero configuration

Apply `@stet.once` with no arguments to use all defaults — all parameters as the key, store in `_stet_store.csv`:

```python
import stet

@stet.once
def run_experiment(alpha, seed):
    ...
```

## Specify a store

Pass `store=` to control where runs are recorded:

```python
@stet.once(store='markov_runs.csv')
def run_experiment(alpha, seed):
    ...
```

The backend is selected from the file extension. See [Choose a Backend](choose-a-backend.md).

## Specify key parameters

Pass `key=` to declare which parameters define experiment identity. Parameters not in `key` are ignored for the purpose of deciding whether a run is skipped:

```python
@stet.once(store='markov_runs.csv', key=['alpha', 'seed'])
def run_experiment(alpha, seed, n_iter=1000):
    ...
```

See [Choose Key Parameters](choose-key-parameters.md) for guidance on what to include.
