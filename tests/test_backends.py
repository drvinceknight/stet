"""Tests for all storage backends."""

from __future__ import annotations

from pathlib import Path

import pytest

from stet.backends._csv import CsvBackend
from stet.backends._json import JsonBackend
from stet.backends._sqlite import SqliteBackend

BACKENDS = [
    ("csv", CsvBackend),
    ("json", JsonBackend),
    ("sqlite", SqliteBackend),
]


@pytest.mark.parametrize("ext,cls", BACKENDS)
def test_has_empty(tmp_path: Path, ext: str, cls: type) -> None:
    backend = cls(tmp_path / f"store.{ext}")
    assert not backend.has({"x": 1})


@pytest.mark.parametrize("ext,cls", BACKENDS)
def test_load_empty(tmp_path: Path, ext: str, cls: type) -> None:
    backend = cls(tmp_path / f"store.{ext}")
    assert backend.load() == []


@pytest.mark.parametrize("ext,cls", BACKENDS)
def test_record_and_has(tmp_path: Path, ext: str, cls: type) -> None:
    backend = cls(tmp_path / f"store.{ext}")
    backend.record({"alpha": 0.1, "beta": 2})
    assert backend.has({"alpha": 0.1, "beta": 2})
    assert not backend.has({"alpha": 0.1, "beta": 3})


@pytest.mark.parametrize("ext,cls", BACKENDS)
def test_load(tmp_path: Path, ext: str, cls: type) -> None:
    backend = cls(tmp_path / f"store.{ext}")
    backend.record({"x": 1})
    backend.record({"x": 2})
    records = backend.load()
    assert len(records) == 2


@pytest.mark.parametrize("ext,cls", BACKENDS)
def test_timestamp_present(tmp_path: Path, ext: str, cls: type) -> None:
    backend = cls(tmp_path / f"store.{ext}")
    backend.record({"x": 1})
    records = backend.load()
    assert "_stet_timestamp" in records[0]


@pytest.mark.parametrize("ext,cls", BACKENDS)
def test_remove(tmp_path: Path, ext: str, cls: type) -> None:
    backend = cls(tmp_path / f"store.{ext}")
    backend.record({"x": 1})
    backend.record({"x": 2})
    backend.remove({"x": "1"})
    assert not backend.has({"x": 1})
    assert backend.has({"x": 2})


@pytest.mark.parametrize("ext,cls", BACKENDS)
def test_clear(tmp_path: Path, ext: str, cls: type) -> None:
    backend = cls(tmp_path / f"store.{ext}")
    backend.record({"x": 1})
    backend.clear()
    assert backend.load() == []


@pytest.mark.parametrize("ext,cls", BACKENDS)
def test_clear_nonexistent(tmp_path: Path, ext: str, cls: type) -> None:
    backend = cls(tmp_path / f"store.{ext}")
    backend.clear()  # should not raise


@pytest.mark.parametrize("ext,cls", BACKENDS)
def test_remove_nonexistent(tmp_path: Path, ext: str, cls: type) -> None:
    backend = cls(tmp_path / f"store.{ext}")
    backend.remove({"x": "999"})  # should not raise


def test_parquet_backend(tmp_path: Path) -> None:
    pytest.importorskip("pyarrow")
    from stet.backends._parquet import ParquetBackend

    backend = ParquetBackend(tmp_path / "store.parquet")
    backend.record({"alpha": 0.1})
    assert backend.has({"alpha": 0.1})
    records = backend.load()
    assert len(records) == 1
    assert "_stet_timestamp" in records[0]
    backend.remove({"alpha": "0.1"})
    assert not backend.has({"alpha": 0.1})
    backend.record({"alpha": 0.5})
    backend.clear()
    assert not backend.path.exists()


def test_get_backend_csv(tmp_path: Path) -> None:
    from stet.backends import get_backend

    b = get_backend(tmp_path / "store.csv")
    assert isinstance(b, CsvBackend)


def test_get_backend_json(tmp_path: Path) -> None:
    from stet.backends import get_backend

    b = get_backend(tmp_path / "store.json")
    assert isinstance(b, JsonBackend)


def test_get_backend_sqlite(tmp_path: Path) -> None:
    from stet.backends import get_backend

    b = get_backend(tmp_path / "store.sqlite")
    assert isinstance(b, SqliteBackend)


def test_get_backend_unsupported(tmp_path: Path) -> None:
    from stet.backends import get_backend

    with pytest.raises(ValueError, match="Unsupported"):
        get_backend(tmp_path / "store.xyz")


def test_get_backend_parquet(tmp_path: Path) -> None:
    pytest.importorskip("pyarrow")
    from stet.backends import get_backend
    from stet.backends._parquet import ParquetBackend

    b = get_backend(tmp_path / "store.parquet")
    assert isinstance(b, ParquetBackend)


def test_csv_has_missing_column(tmp_path: Path) -> None:
    """has() returns False when a key column is absent from the CSV."""
    backend = CsvBackend(tmp_path / "store.csv")
    backend.record({"x": 1})
    assert not backend.has({"z": 1})


def test_parquet_load_empty(tmp_path: Path) -> None:
    pytest.importorskip("pyarrow")
    from stet.backends._parquet import ParquetBackend

    backend = ParquetBackend(tmp_path / "store.parquet")
    assert backend.load() == []


def test_parquet_has_missing_column(tmp_path: Path) -> None:
    pytest.importorskip("pyarrow")
    from stet.backends._parquet import ParquetBackend

    backend = ParquetBackend(tmp_path / "store.parquet")
    backend.record({"x": 1})
    assert not backend.has({"z": 1})


def test_parquet_remove_empty(tmp_path: Path) -> None:
    pytest.importorskip("pyarrow")
    from stet.backends._parquet import ParquetBackend

    backend = ParquetBackend(tmp_path / "store.parquet")
    backend.remove({"x": "1"})  # should not raise


def test_parquet_clear_nonexistent(tmp_path: Path) -> None:
    pytest.importorskip("pyarrow")
    from stet.backends._parquet import ParquetBackend

    backend = ParquetBackend(tmp_path / "store.parquet")
    backend.clear()  # should not raise


def test_sqlite_alter_table(tmp_path: Path) -> None:
    """Recording with a new column on an existing table triggers ALTER TABLE."""
    backend = SqliteBackend(tmp_path / "store.sqlite")
    backend.record({"x": 1})
    backend.record({"x": 2, "y": 3})  # 'y' column added via ALTER TABLE
    assert backend.has({"x": 2})


def _make_empty_db(path: Path) -> None:
    import sqlite3

    sqlite3.connect(path).close()


def test_sqlite_has_on_empty_db(tmp_path: Path) -> None:
    """has() returns False when the DB exists but has no table."""
    store = tmp_path / "store.sqlite"
    _make_empty_db(store)
    backend = SqliteBackend(store)
    assert not backend.has({"x": 1})


def test_sqlite_load_on_empty_db(tmp_path: Path) -> None:
    """load() returns [] when the DB exists but has no table."""
    store = tmp_path / "store.sqlite"
    _make_empty_db(store)
    backend = SqliteBackend(store)
    assert backend.load() == []


def test_sqlite_remove_on_empty_db(tmp_path: Path) -> None:
    """remove() does not raise when the DB exists but has no table."""
    store = tmp_path / "store.sqlite"
    _make_empty_db(store)
    backend = SqliteBackend(store)
    backend.remove({"x": "1"})  # should not raise


def test_concurrent_writes(tmp_path: Path) -> None:
    """Concurrent writes must not corrupt the store."""
    import threading

    store = tmp_path / "store.csv"
    backend = CsvBackend(store)
    errors: list[Exception] = []

    def write(i: int) -> None:
        try:
            backend.record({"x": i})
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=write, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    records = backend.load()
    assert len(records) == 20
