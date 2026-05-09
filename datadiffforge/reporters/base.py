"""
Abstract reporter interface for DataDiffForge.

All reporters must implement the ReporterInterface to ensure consistent
output formatting across different output formats.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.types import DiffResult


class ReporterInterface(ABC):
    """
    Abstract base class for all diff reporters.

    Each reporter must implement the report() method to format
    diff results for a specific output format.
    """

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return the name of the output format (e.g., 'terminal')."""
        ...

    @abstractmethod
    def report(self, result: "DiffResult", **kwargs) -> str:
        """
        Format a DiffResult for output.

        Args:
            result: The diff result to format.
            **kwargs: Additional formatting options.

        Returns:
            Formatted string representation of the diff result.
        """
        ...
