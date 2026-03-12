"""Storage backends for the stet library."""

from __future__ import annotations

from pathlib import Path

from stet.backends._base import BaseBackend
from stet.backends._csv import CsvBackend
from stet.backends._json import JsonBackend
from stet.backends._sqlite import SqliteBackend

__all__ = ["BaseBackend", "CsvBackend", "JsonBackend", "SqliteBackend", "get_backend"]

_EXTENSION_MAP: dict[str, type[BaseBackend]] = {
    ".csv": CsvBackend,
    ".json": JsonBackend,
    ".sqlite": SqliteBackend,
    ".db": SqliteBackend,
}


def get_backend(path: Path) -> BaseBackend:
    """Return the appropriate backend for the given file path.

    The backend is selected based on the file extension:

    - ``.csv`` → :class:`~stet.backends._csv.CsvBackend`
    - ``.parquet`` → :class:`~stet.backends._parquet.ParquetBackend`
    - ``.sqlite`` / ``.db`` → :class:`~stet.backends._sqlite.SqliteBackend`
    - ``.json`` → :class:`~stet.backends._json.JsonBackend`

    Args:
        path: Path to the store file.

    Returns:
        A backend instance for the given file extension.

    Raises:
        ValueError: If the file extension is not supported.
    """
    ext = path.suffix.lower()

    if ext == ".parquet":
        from stet.backends._parquet import ParquetBackend

        return ParquetBackend(path)

    cls = _EXTENSION_MAP.get(ext)
    if cls is None:
        supported = ", ".join(sorted(_EXTENSION_MAP) + [".parquet"])
        raise ValueError(
            f"Unsupported store extension: {ext!r}. Supported: {supported}"
        )
    return cls(path)
