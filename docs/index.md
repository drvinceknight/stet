# once

**once** is a Python library that solves a common problem in computational research: when a long-running experiment script is re-run — whether after a crash, a time limit, or deliberately to extend a sweep — it should automatically skip any experiments that have already been completed.

## The Problem

You're running a parameter sweep over thousands of combinations. Your script stops — maybe it crashed, maybe you killed it, maybe you just want to add more parameter values. You restart it and it starts over from the beginning, re-running everything.

## The Solution

Decorate your experiment function with `@once`:

```python
import once
import numpy as np

@once.once(store='markov_runs.csv', key=['alpha', 'n_states', 'seed'])
def solve_markov(alpha, n_states, seed, n_iter=1000):
    # expensive computation here
    result = run_chain(alpha, n_states, seed, n_iter)
    # write your own output
    with open('markov_output.csv', 'a') as f:
        f.write(f"{alpha},{n_states},{seed},{result}\n")

for alpha in np.linspace(0.01, 1.0, 50):
    for n_states in [10, 50, 100]:
        for seed in range(20):
            solve_markov(alpha=alpha, n_states=n_states, seed=seed)
```

On restart, any already-completed `(alpha, n_states, seed)` combinations are skipped automatically.

## Installation

```
$ uv add once
$ uv add once[parquet]  # with parquet support
```

or

```
$ python -m pip install once
$ python -m pip install once[parquet]  # with parquet support
```

## Quick Start

```python
import once

@once.once(store='_once_store.csv', key=['alpha', 'beta'])
def run_experiment(alpha, beta, n_steps=1000):
    # your computation here
    pass
```

See the [Getting Started tutorial](tutorials/getting-started.md) for a complete walkthrough.
