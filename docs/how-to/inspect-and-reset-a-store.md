# Inspect a Store

## Check progress with `stet.status()`

```python
import stet

stet.status()                  # default store
stet.status('markov_runs.csv') # named store
```

Output:

```
[stet] Store: _stet_store.csv
[stet] 142 completed experiments recorded
[stet] Last run: 2024-11-03T14:22:01
[stet] Key columns: alpha, beta, n_steps
```

## Inspect the store directly

The store is a plain file; you can load it as a list of dicts and work with it however
you like:

```python
from stet.backends import get_backend
from pathlib import Path

backend = get_backend(Path('_stet_store.csv'))
records = backend.load()
print(records[:3])
```
