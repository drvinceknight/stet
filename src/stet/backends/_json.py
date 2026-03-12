"""JSON backend using Python's built-in json module."""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any

import filelock

from stet.backends._base import BaseBackend


class JsonBackend(BaseBackend):
    """Store experiment records in a JSON file.

    Uses Python's built-in :mod:`json`. No extra dependencies required.

    Args:
        path: Path to the ``.json`` file. Created on first write.

    Example:
        ```python
        from stet.backends._json import JsonBackend
        from pathlib import Path

        backend = JsonBackend(Path('_stet_store.json'))
        backend.record({'alpha': 0.1, 'beta': 2})
        backend.has({'alpha': 0.1, 'beta': 2})  # True
        ```
    """

    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self._lock = filelock.FileLock(str(path) + ".lock")

    def _read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with open(self.path) as f:
            data = json.load(f)
        return data if isinstance(data, list) else []

    def _write(self, records: list[dict[str, Any]]) -> None:
        with open(self.path, "w") as f:
            json.dump(records, f, indent=2, default=str)

    def has(self, key_dict: dict[str, Any]) -> bool:
        """Check if key combination exists in the JSON store.

        Args:
            key_dict: Parameter names and values to look up.

        Returns:
            True if this combination has been recorded, False otherwise.
        """
        with self._lock:
            records = self._read()
        str_key = {k: str(v) for k, v in key_dict.items()}
        for rec in records:
            if all(str(rec.get(k)) == v for k, v in str_key.items()):
                return True
        return False

    def record(self, key_dict: dict[str, Any]) -> None:
        """Append a key combination to the JSON store.

        Args:
            key_dict: Parameter names and values to record.
        """
        row: dict[str, Any] = {k: str(v) for k, v in key_dict.items()}
        row["_stet_timestamp"] = datetime.datetime.now(datetime.UTC).isoformat()
        with self._lock:
            records = self._read()
            records.append(row)
            self._write(records)

    def load(self) -> list[dict[str, Any]]:
        """Return all records from the JSON store.

        Returns:
            List of dicts, each representing one recorded experiment run.
        """
        with self._lock:
            return self._read()

    def remove(self, key_dict: dict[str, Any]) -> None:
        """Remove a specific key combination from the JSON store.

        Args:
            key_dict: The exact key combination to remove.
        """
        str_key = {k: str(v) for k, v in key_dict.items()}
        with self._lock:
            records = self._read()
            records = [
                r
                for r in records
                if not all(str(r.get(k)) == v for k, v in str_key.items())
            ]
            self._write(records)

    def clear(self) -> None:
        """Remove all records from the JSON store."""
        with self._lock:
            if self.path.exists():
                self.path.unlink()
