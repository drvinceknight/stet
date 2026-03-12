# Specify a Store

## Use the default

If you don't specify a store, `stet` creates `_stet_store.csv` in the current working
directory. This is fine for single-script projects where everything runs from one place:

```python
@stet.once
def run_experiment(alpha, seed):
    ...

stet.status()   # reads _stet_store.csv
stet.reset()    # clears _stet_store.csv
```

## Name the store explicitly

Pass `store=` to control the file name and location:

```python
@stet.once(store='markov_runs.csv', key=['alpha', 'seed'])
def solve_markov(alpha, seed):
    ...

stet.status('markov_runs.csv')
stet.reset('markov_runs.csv')
```

Explicit names are useful when you have multiple independent experiments in the same
project that should track runs separately.

## Choose a location

The `store` path can be relative or absolute:

```python
# next to your script
@stet.once(store='runs/markov.csv')

# shared across scripts in a project
@stet.once(store='/data/experiments/markov_runs.sqlite')
```

## Choose a format

The backend is selected from the file extension; just change the extension to switch:

```python
@stet.once(store='markov_runs.sqlite')   # SQLite - better for parallel runs
@stet.once(store='markov_runs.json')     # JSON - no extra dependencies
@stet.once(store='markov_runs.parquet')  # Parquet - compact, requires stet[parquet]
```

See [Choose a Backend](choose-a-backend.md) for guidance on which format to use.
