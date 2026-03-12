"""Tests for stet._utils (status and reset)."""

from __future__ import annotations

from pathlib import Path

import pytest

import stet


def test_status_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        stet.status(tmp_path / "nonexistent.csv")


def test_status_default_store(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)

    @stet.once
    def run(x: int) -> None:
        pass

    run(x=1)
    stet.status()
    out = capsys.readouterr().out
    assert "1 completed" in out


def test_reset_default_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    @stet.once
    def run(x: int) -> None:
        pass

    run(x=1)
    stet.reset()
    assert not (tmp_path / "_stet_store.csv").exists()


def test_status_csv(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    store = tmp_path / "results.csv"

    @stet.once(store=store, key=["alpha"])
    def run(alpha: float, beta: int) -> None:
        pass

    run(alpha=0.1, beta=1)
    stet.status(store)
    out = capsys.readouterr().out
    assert "1 completed" in out
    assert "alpha" in out


def test_status_shows_last_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = tmp_path / "results.csv"

    @stet.once(store=store)
    def run(x: int) -> None:
        pass

    run(x=1)
    run(x=2)
    stet.status(store)
    out = capsys.readouterr().out
    assert "2 completed" in out
    assert "Last run" in out


def test_reset_all(tmp_path: Path) -> None:
    store = tmp_path / "results.csv"

    @stet.once(store=store)
    def run(x: int) -> None:
        pass

    run(x=1)
    run(x=2)

    stet.reset(store)
    assert not store.exists()


def test_reset_specific_key(tmp_path: Path) -> None:
    store = tmp_path / "results.csv"

    @stet.once(store=store)
    def run(x: int) -> None:
        pass

    run(x=1)
    run(x=2)

    stet.reset(store, {"x": "1"})

    from stet.backends import get_backend

    backend = get_backend(store)
    records = backend.load()
    xs = [r["x"] for r in records]
    assert "1" not in xs
    assert "2" in xs


def test_reset_all_noninteractive(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """In non-interactive mode (stdin not a tty) reset should not prompt."""
    store = tmp_path / "results.csv"

    @stet.once(store=store)
    def run(x: int) -> None:
        pass

    run(x=5)
    stet.reset(store)
    out = capsys.readouterr().out
    assert "cleared" in out


def test_reset_all_interactive_yes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Interactive reset with 'y' clears the store."""
    store = tmp_path / "results.csv"

    @stet.once(store=store)
    def run(x: int) -> None:
        pass

    run(x=1)
    fake_tty = type("FakeTTY", (), {"isatty": lambda self: True})()
    monkeypatch.setattr("sys.stdin", fake_tty)
    monkeypatch.setattr("builtins.input", lambda _: "y")
    stet.reset(store)
    assert not store.exists()
    out = capsys.readouterr().out
    assert "cleared" in out


def test_reset_all_interactive_no(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Interactive reset with 'n' aborts without clearing."""
    store = tmp_path / "results.csv"

    @stet.once(store=store)
    def run(x: int) -> None:
        pass

    run(x=1)
    fake_tty = type("FakeTTY", (), {"isatty": lambda self: True})()
    monkeypatch.setattr("sys.stdin", fake_tty)
    monkeypatch.setattr("builtins.input", lambda _: "n")
    stet.reset(store)
    assert store.exists()
    out = capsys.readouterr().out
    assert "Aborted" in out
