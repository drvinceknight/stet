"""SQLite backend using Python's built-in sqlite3."""

from __future__ import annotations

import datetime
import sqlite3
from pathlib import Path
from typing import Any

import filelock

from stet.backends._base import BaseBackend

_TABLE = "stet_records"


class SqliteBackend(BaseBackend):
    """Store experiment records in a SQLite database.

    Uses Python's built-in :mod:`sqlite3`. No extra dependencies required.

    Args:
        path: Path to the ``.sqlite`` or ``.db`` file. Created on first write.

    Example:
        ```python
        from stet.backends._sqlite import SqliteBackend
        from pathlib import Path

        backend = SqliteBackend(Path('_stet_store.sqlite'))
        backend.record({'alpha': 0.1, 'beta': 2})
        backend.has({'alpha': 0.1, 'beta': 2})
        ```
    """

    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self._lock = filelock.FileLock(str(path) + ".lock")

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_table(self, conn: sqlite3.Connection, columns: list[str]) -> None:
        cols_sql = ", ".join(f'"{c}" TEXT' for c in [*columns, "_stet_timestamp"])
        conn.execute(f"CREATE TABLE IF NOT EXISTS {_TABLE} ({cols_sql})")
        existing = {row[1] for row in conn.execute(f"PRAGMA table_info({_TABLE})")}
        for col in [*columns, "_stet_timestamp"]:
            if col not in existing:
                conn.execute(f'ALTER TABLE {_TABLE} ADD COLUMN "{col}" TEXT')

    def has(self, key_dict: dict[str, Any]) -> bool:
        """Check if key combination exists in the SQLite store.

        Args:
            key_dict: Parameter names and values to look up.

        Returns:
            True if this combination has been recorded, False otherwise.
        """
        with self._lock:
            if not self.path.exists():
                return False
            with self._connect() as conn:
                try:
                    where = " AND ".join(f'"{k}" = ?' for k in key_dict)
                    vals = [str(v) for v in key_dict.values()]
                    row = conn.execute(
                        f"SELECT 1 FROM {_TABLE} WHERE {where} LIMIT 1", vals
                    ).fetchone()
                    return row is not None
                except sqlite3.OperationalError:
                    return False

    def record(self, key_dict: dict[str, Any]) -> None:
        """Insert a key combination into the SQLite store.

        Args:
            key_dict: Parameter names and values to record.
        """
        row = {k: str(v) for k, v in key_dict.items()}
        row["_stet_timestamp"] = datetime.datetime.now(datetime.UTC).isoformat()
        with self._lock:
            with self._connect() as conn:
                self._ensure_table(conn, list(key_dict.keys()))
                cols = ", ".join(f'"{c}"' for c in row)
                placeholders = ", ".join("?" for _ in row)
                conn.execute(
                    f"INSERT INTO {_TABLE} ({cols}) VALUES ({placeholders})",
                    list(row.values()),
                )

    def load(self) -> list[dict[str, Any]]:
        """Return all records from the SQLite store.

        Returns:
            List of dicts, each representing one recorded experiment run.
        """
        with self._lock:
            if not self.path.exists():
                return []
            with self._connect() as conn:
                try:
                    rows = conn.execute(f"SELECT * FROM {_TABLE}").fetchall()
                    return [dict(r) for r in rows]
                except sqlite3.OperationalError:
                    return []

    def remove(self, key_dict: dict[str, Any]) -> None:
        """Remove a specific key combination from the SQLite store.

        Args:
            key_dict: The exact key combination to remove.
        """
        with self._lock:
            if not self.path.exists():
                return
            with self._connect() as conn:
                try:
                    where = " AND ".join(f'"{k}" = ?' for k in key_dict)
                    vals = [str(v) for v in key_dict.values()]
                    conn.execute(f"DELETE FROM {_TABLE} WHERE {where}", vals)
                except sqlite3.OperationalError:
                    pass

    def clear(self) -> None:
        """Remove all records from the SQLite store."""
        with self._lock:
            if not self.path.exists():
                return
            with self._connect() as conn:
                conn.execute(f"DROP TABLE IF EXISTS {_TABLE}")
