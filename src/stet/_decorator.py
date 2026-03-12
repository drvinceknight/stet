"""Core decorator implementation."""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable
from pathlib import Path
from typing import Any

from stet.backends import get_backend


def _bind_args(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    sig = inspect.signature(func)
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()
    return dict(bound.arguments)


def _extract_key(
    all_args: dict[str, Any],
    key: list[str] | None,
) -> dict[str, Any]:
    if key is None:
        return all_args
    return {k: all_args[k] for k in key if k in all_args}


def _format_key(func_name: str, key_dict: dict[str, Any]) -> str:
    params = ", ".join(f"{k}={v!r}" for k, v in key_dict.items())
    return f"{func_name}({params})"


class _OnceDecorator:
    def __init__(self, store: str | Path, key: list[str] | None) -> None:
        self._store = Path(store)
        self._key = key

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        backend = get_backend(self._store)
        key = self._key

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            all_args = _bind_args(func, args, kwargs)
            key_dict = _extract_key(all_args, key)

            if backend.has(key_dict):
                label = _format_key(getattr(func, "__name__", repr(func)), key_dict)
                print(f"[stet] Skipping {label}")
                return None

            result = func(*args, **kwargs)
            backend.record(key_dict)
            return result

        return wrapper


def once(
    func: Callable[..., Any] | None = None,
    *,
    store: str | Path = "_stet_store.csv",
    key: list[str] | None = None,
) -> Any:
    """Decorator that skips already-completed experiment runs.

    Tracks which parameter combinations have been executed and skips them
    on subsequent calls. The function's return value is not saved; only
    whether the combination has been run.

    Can be used in three styles:

    Style 1 - zero config::

        @once
        def run_experiment(alpha, beta):
            ...

    Style 2 - specify store::

        @once(store='_stet_store.csv')
        def run_experiment(alpha, beta):
            ...

    Style 3 - full control::

        @once(store='_stet_store.csv', key=['alpha', 'beta'])
        def run_experiment(alpha, beta, n_steps):
            ...

    Args:
        func: The function to decorate (when used without parentheses).
        store: Path to the store file. Backend is inferred from extension:
            ``.csv``, ``.parquet``, ``.sqlite``, ``.json``.
            Defaults to ``_stet_store.csv`` in the current directory.
        key: Parameter names that uniquely identify a run. If omitted,
            all parameters are used.

    Returns:
        The decorated function (or a decorator if called with arguments).

    Example:
        ```python
        @once(store='_stet_store.csv', key=['alpha', 'seed'])
        def run_experiment(alpha, seed, n_iter=1000):
            pass

        run_experiment(alpha=0.1, seed=42)
        run_experiment(alpha=0.1, seed=42)
        ```
    """
    decorator = _OnceDecorator(store=store, key=key)

    if func is not None:
        return decorator(func)

    return decorator
