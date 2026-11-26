# Decorate a Function with `once`

## Zero configuration

Apply `@stet.once` with no arguments to use all defaults: all parameters as the key,
store in `_stet_store.csv`:

```python
import stet


@stet.once
def run_experiment(alpha, seed): ...
```

## Specify a store

Pass `store=` to control where runs are recorded:

```python
@stet.once(store="markov_runs.csv")
def run_experiment(alpha, seed): ...
```

The backend is selected from the file extension.
See [Choose a Backend](choose-a-backend.md).

## Specify key parameters

Pass `key=` to declare which parameters define experiment identity. Parameters not in
`key` are ignored for the purpose of deciding whether a run is skipped:

```python
@stet.once(store="markov_runs.csv", key=["alpha", "seed"])
def run_experiment(alpha, seed, n_iter=1000): ...
```

See [Choose Key Parameters](choose-key-parameters.md) for guidance on what to include.

## Silence skip messages

Pass `verbose=False` to stop `stet` printing a message each time a run is skipped:

```python
@stet.once(store="markov_runs.csv", key=["alpha", "seed"], verbose=False)
def run_experiment(alpha, seed, n_iter=1000): ...
```

This is useful when running in parallel, where messages from different processes
interleave. See [Use with Multiprocessing](use-with-multiprocessing.md).
