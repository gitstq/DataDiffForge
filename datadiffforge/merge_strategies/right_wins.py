"""
Right Wins merge strategy.

When a conflict is detected, the right (target) value always takes priority.
This is useful when you want to preserve changes from the target file.
"""

import copy
from typing import Any

from .base import StrategyInterface


class RightWinsStrategy(StrategyInterface):
    """
    Merge strategy where the right/target value always wins.

    In case of a conflict, the right value is used unconditionally.
    """

    @property
    def name(self) -> str:
        """Return 'right-wins'."""
        return "right-wins"

    def resolve(self, left: Any, right: Any, base: Any = None) -> Any:
        """
        Return the right value.

        Args:
            left: The left/source value (ignored).
            right: The right/target value.
            base: The base value (unused).

        Returns:
            A deep copy of the right value.
        """
        return copy.deepcopy(right)

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
