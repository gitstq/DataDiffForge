"""
Abstract parser interface for DataDiffForge.

All parsers must implement the ParserInterface to ensure consistent
load/dump behavior across different file formats.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class ParserInterface(ABC):
    """
    Abstract base class for all data format parsers.

    Each parser must implement load() and dump() methods to support
    reading and writing structured data in a specific format.
    """

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return the name of the format this parser handles (e.g., 'json')."""
        ...

    @property
    @abstractmethod
    def file_extensions(self) -> list:
        """Return a list of file extensions this parser handles (e.g., ['.json'])."""
        ...

    @abstractmethod
    def load(self, content: str) -> Any:
        """
        Parse a string content into a Python data structure.

        Args:
            content: The string content to parse.

        Returns:
            The parsed Python data structure (dict, list, or primitive).
        """
        ...

    @abstractmethod
    def dump(self, data: Any) -> str:
        """
        Serialize a Python data structure to a string.

        Args:
            data: The Python data structure to serialize.

        Returns:
            The serialized string representation.
        """
        ...

    def load_file(self, filepath: str) -> Any:
        """
        Load and parse a file.

        Args:
            filepath: Path to the file to load.

        Returns:
            The parsed Python data structure.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return self.load(f.read())

    def dump_file(self, data: Any, filepath: str) -> None:
        """
        Serialize data and write to a file.

        Args:
            data: The Python data structure to serialize.
            filepath: Path to the output file.
        """
        content = self.dump(data)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
