"""Abstract base class for stet storage backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseBackend(ABC):
    """Abstract base class defining the backend interface.

    All backends must implement :meth:`has`, :meth:`record`,
    :meth:`load`, :meth:`remove`, and :meth:`clear`.

    Args:
        path: Path to the store file.
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    @abstractmethod
    def has(self, key_dict: dict[str, Any]) -> bool:
        """Check if a key combination exists in the store.

        Args:
            key_dict: Parameter names and values to look up.

        Returns:
            True if this combination has been recorded, False otherwise.
        """

    @abstractmethod
    def record(self, key_dict: dict[str, Any]) -> None:
        """Write a key combination to the store.

        Adds ``_stet_timestamp`` with the current UTC time.

        Args:
            key_dict: Parameter names and values to record.
        """

    @abstractmethod
    def load(self) -> list[dict[str, Any]]:
        """Return all stored records.

        Returns:
            List of dicts, each representing one recorded experiment run.
        """

    @abstractmethod
    def remove(self, key_dict: dict[str, Any]) -> None:
        """Remove a specific key combination from the store.

        Args:
            key_dict: The exact key combination to remove.
        """

    @abstractmethod
    def clear(self) -> None:
        """Remove all records from the store."""
