"""stet: persistent memoization by parameter identity.

Decorates experiment functions so they skip already-completed runs on restart.

Example:
    ```python
    import stet

    @stet.once(store='_stet_store.csv', key=['alpha', 'beta'])
    def run_experiment(alpha, beta, n_steps):
        ...
    ```
"""

from stet._decorator import once
from stet._utils import reset, status

__all__ = ["once", "status", "reset"]
