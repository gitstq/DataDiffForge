"""
Keep Both merge strategy.

When a conflict is detected, this strategy attempts to keep both values.
For lists, values are concatenated. For dicts, they are merged. For
primitives, both values are returned as a list.
"""

import copy
from typing import Any

from .base import StrategyInterface


class KeepBothStrategy(StrategyInterface):
    """
    Merge strategy that keeps both values when a conflict is detected.

    Behavior by type:
    - Lists: Concatenate (left + right)
    - Dicts: Merge (right overrides left for duplicate keys)
    - Primitives: Return as a two-element list [left, right]
    """

    @property
    def name(self) -> str:
        """Return 'keep-both'."""
        return "keep-both"

    def resolve(self, left: Any, right: Any, base: Any = None) -> Any:
        """
        Keep both values by combining them.

        Args:
            left: The left/source value.
            right: The right/target value.
            base: The base value (unused in this strategy).

        Returns:
            Combined value depending on types.
        """
        # Both are lists - concatenate
        if isinstance(left, list) and isinstance(right, list):
            return copy.deepcopy(left) + copy.deepcopy(right)

        # Both are dicts - merge
        if isinstance(left, dict) and isinstance(right, dict):
            merged = copy.deepcopy(left)
            merged.update(copy.deepcopy(right))
            return merged

        # For primitives or mixed types, return as a list
        return [copy.deepcopy(left), copy.deepcopy(right)]

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
