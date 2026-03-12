"""Parquet backend using pandas + pyarrow."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

import filelock

from stet.backends._base import BaseBackend


class ParquetBackend(BaseBackend):
    """Store experiment records in a Parquet file using pandas and pyarrow.

    Requires the ``parquet`` extra: ``uv add stet[parquet]``.

    Args:
        path: Path to the ``.parquet`` file. Created on first write.

    Example:
        ```python
        from stet.backends._parquet import ParquetBackend
        from pathlib import Path

        backend = ParquetBackend(Path('_stet_store.parquet'))
        backend.record({'alpha': 0.1, 'beta': 2})
        backend.has({'alpha': 0.1, 'beta': 2})
        ```
    """

    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self._lock = filelock.FileLock(str(path) + ".lock")

    def _read(self) -> Any:
        import pandas as pd

        if not self.path.exists():
            return pd.DataFrame()
        return pd.read_parquet(self.path)

    def has(self, key_dict: dict[str, Any]) -> bool:
        """Check if key combination exists in the Parquet store.

        Args:
            key_dict: Parameter names and values to look up.

        Returns:
            True if this combination has been recorded, False otherwise.
        """
        import pandas as pd

        with self._lock:
            df = self._read()
        if df.empty:
            return False
        mask = pd.Series([True] * len(df), dtype=bool)
        for col, val in key_dict.items():
            if col not in df.columns:
                return False
            mask = mask & (df[col].astype(str) == str(val))
        return bool(mask.any())

    def record(self, key_dict: dict[str, Any]) -> None:
        """Append a key combination to the Parquet store.

        Args:
            key_dict: Parameter names and values to record.
        """
        import pandas as pd

        row = {k: str(v) for k, v in key_dict.items()}
        row["_stet_timestamp"] = datetime.datetime.now(datetime.UTC).isoformat()
        with self._lock:
            df = self._read()
            new_row = pd.DataFrame([row])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_parquet(self.path, index=False)

    def load(self) -> list[dict[str, Any]]:
        """Return all records from the Parquet store.

        Returns:
            List of dicts, each representing one recorded experiment run.
        """
        with self._lock:
            df = self._read()
        if df.empty:
            return []
        return df.to_dict(orient="records")

    def remove(self, key_dict: dict[str, Any]) -> None:
        """Remove a specific key combination from the Parquet store.

        Args:
            key_dict: The exact key combination to remove.
        """
        import pandas as pd

        with self._lock:
            df = self._read()
            if df.empty:
                return
            mask = pd.Series([True] * len(df), dtype=bool)
            for col, val in key_dict.items():
                if col in df.columns:
                    mask = mask & (df[col].astype(str) == str(val))
            df = df[~mask]
            df.to_parquet(self.path, index=False)

    def clear(self) -> None:
        """Remove all records from the Parquet store."""
        with self._lock:
            if self.path.exists():
                self.path.unlink()
