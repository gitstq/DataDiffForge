"""
Abstract merge strategy interface for DataDiffForge.

All merge strategies must implement the StrategyInterface to ensure
consistent behavior across different merge approaches.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class StrategyInterface(ABC):
    """
    Abstract base class for all merge strategies.

    Each strategy must implement the resolve() method to determine
    how to handle conflicts between left and right values.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this strategy (e.g., 'left-wins')."""
        ...

    @abstractmethod
    def resolve(self, left: Any, right: Any, base: Any = None) -> Any:
        """
        Resolve a conflict between two values.

        Args:
            left: The left/source value.
            right: The right/target value.
            base: The base value (for three-way merge, if available).

        Returns:
            The resolved value.
        """
        ...

    @abstractmethod
    def can_merge(self, left: Any, right: Any) -> bool:
        """
        Check if this strategy can merge the given values.

        Some strategies may only work with specific types of values.

        Args:
            left: The left value.
            right: The right value.

        Returns:
            True if this strategy can handle the merge.
        """
        ...
