"""
Left Wins merge strategy.

When a conflict is detected, the left (source) value always takes priority.
This is useful when you want to preserve changes from the source file.
"""

import copy
from typing import Any

from .base import StrategyInterface


class LeftWinsStrategy(StrategyInterface):
    """
    Merge strategy where the left/source value always wins.

    In case of a conflict, the left value is used unconditionally.
    """

    @property
    def name(self) -> str:
        """Return 'left-wins'."""
        return "left-wins"

    def resolve(self, left: Any, right: Any, base: Any = None) -> Any:
        """
        Return the left value.

        Args:
            left: The left/source value.
            right: The right/target value (ignored).
            base: The base value (unused).

        Returns:
            A deep copy of the left value.
        """
        return copy.deepcopy(left)

    def can_merge(self, left: Any, right: Any) -> bool:
        """
        This strategy can merge any two values.

        Args:
            left: The left value.
            right: The right value.

        Returns:
            Always True.
        """
        return True
