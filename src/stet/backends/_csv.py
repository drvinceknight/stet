"""CSV backend using pandas."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

import filelock
import pandas as pd

from stet.backends._base import BaseBackend


class CsvBackend(BaseBackend):
    """Store experiment records in a CSV file using pandas.

    Args:
        path: Path to the ``.csv`` file. Created on first write.

    Example:
        ```python
        from stet.backends import CsvBackend
        from pathlib import Path

        backend = CsvBackend(Path('_stet_store.csv'))
        backend.record({'alpha': 0.1, 'beta': 2})
        backend.has({'alpha': 0.1, 'beta': 2})
        ```
    """

    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self._lock = filelock.FileLock(str(path) + ".lock")

    def _read(self) -> pd.DataFrame:
        if not self.path.exists():
            return pd.DataFrame()
        return pd.read_csv(self.path, dtype=str)

    def has(self, key_dict: dict[str, Any]) -> bool:
        """Check if key combination exists in the CSV store.

        Args:
            key_dict: Parameter names and values to look up.

        Returns:
            True if this combination has been recorded, False otherwise.
        """
        with self._lock:
            df = self._read()
        if df.empty:
            return False
        cols = list(key_dict.keys())
        missing = [c for c in cols if c not in df.columns]
        if missing:
            return False
        mask = pd.Series([True] * len(df), dtype=bool)
        for col, val in key_dict.items():
            mask = mask & (df[col] == str(val))
        return bool(mask.any())

    def record(self, key_dict: dict[str, Any]) -> None:
        """Append a key combination to the CSV store.

        Args:
            key_dict: Parameter names and values to record.
        """
        row = {k: str(v) for k, v in key_dict.items()}
        row["_stet_timestamp"] = datetime.datetime.now(datetime.UTC).isoformat()
        with self._lock:
            df = self._read()
            new_row = pd.DataFrame([row])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(self.path, index=False)

    def load(self) -> list[dict[str, Any]]:
        """Return all records from the CSV store.

        Returns:
            List of dicts, each representing one recorded experiment run.
        """
        with self._lock:
            df = self._read()
        if df.empty:
            return []
        return df.to_dict(orient="records")

    def remove(self, key_dict: dict[str, Any]) -> None:
        """Remove a specific key combination from the CSV store.

        Args:
            key_dict: The exact key combination to remove.
        """
        with self._lock:
            df = self._read()
            if df.empty:
                return
            mask = pd.Series([True] * len(df), dtype=bool)
            for col, val in key_dict.items():
                if col in df.columns:
                    mask = mask & (df[col] == str(val))
            df = df[~mask]
            df.to_csv(self.path, index=False)

    def clear(self) -> None:
        """Remove all records from the CSV store."""
        with self._lock:
            if self.path.exists():
                self.path.unlink()
