"""Tests for the once decorator."""

from __future__ import annotations

from pathlib import Path

import pytest

import stet


def test_runs_once(tmp_path: Path) -> None:
    store = tmp_path / "store.csv"
    call_count = 0

    @stet.once(store=store)
    def experiment(x: int) -> None:
        nonlocal call_count
        call_count += 1

    experiment(x=1)
    experiment(x=1)
    assert call_count == 1


def test_runs_different_params(tmp_path: Path) -> None:
    store = tmp_path / "store.csv"
    call_count = 0

    @stet.once(store=store)
    def experiment(x: int) -> None:
        nonlocal call_count
        call_count += 1

    experiment(x=1)
    experiment(x=2)
    assert call_count == 2


def test_key_subset(tmp_path: Path) -> None:
    store = tmp_path / "store.csv"
    call_count = 0

    @stet.once(store=store, key=["alpha"])
    def experiment(alpha: float, n_iter: int = 100) -> None:
        nonlocal call_count
        call_count += 1

    experiment(alpha=0.1, n_iter=100)
    experiment(alpha=0.1, n_iter=999)  # different n_iter, same key
    assert call_count == 1


def test_no_parentheses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    call_count = 0

    @stet.once
    def experiment(x: int) -> None:
        nonlocal call_count
        call_count += 1

    experiment(x=42)
    experiment(x=42)
    assert call_count == 1


def test_skip_message(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    store = tmp_path / "store.csv"

    @stet.once(store=store)
    def my_func(a: int) -> None:
        pass

    my_func(a=1)
    my_func(a=1)
    out = capsys.readouterr().out
    assert "[stet] Skipping my_func" in out


def test_return_value_passthrough(tmp_path: Path) -> None:
    store = tmp_path / "store.csv"

    @stet.once(store=store)
    def experiment(x: int) -> int:
        return x * 2

    result = experiment(x=5)
    assert result == 10


def test_second_call_returns_none(tmp_path: Path) -> None:
    store = tmp_path / "store.csv"

    @stet.once(store=store)
    def experiment(x: int) -> int:
        return x * 2

    experiment(x=5)
    result = experiment(x=5)
    assert result is None


def test_positional_args(tmp_path: Path) -> None:
    store = tmp_path / "store.csv"
    call_count = 0

    @stet.once(store=store)
    def experiment(x: int, y: int) -> None:
        nonlocal call_count
        call_count += 1

    experiment(1, 2)
    experiment(1, 2)
    assert call_count == 1


def test_defaults_included_in_key(tmp_path: Path) -> None:
    store = tmp_path / "store.csv"
    call_count = 0

    @stet.once(store=store)
    def experiment(x: int, y: int = 10) -> None:
        nonlocal call_count
        call_count += 1

    experiment(x=1)
    experiment(x=1, y=10)  # same after defaults applied
    assert call_count == 1
