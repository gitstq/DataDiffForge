"""
Smart merge strategy.

An AI-like intelligent merge strategy that analyzes the types and values
of conflicting data to make informed merge decisions.

Rules:
- Numeric values: Average if both changed from base
- Strings: Concatenate with separator if both changed
- Booleans: AND logic
- Lists: Concatenate unique elements
- Dicts: Recursive merge
- Mixed types: Prefer the more specific type
"""

import copy
from typing import Any, Optional

from .base import StrategyInterface


class SmartStrategy(StrategyInterface):
    """
    Intelligent merge strategy that makes context-aware merge decisions.

    Analyzes the types and values of both sides to determine the best
    way to resolve conflicts. Uses heuristics based on data types
    and three-way merge information when available.
    """

    @property
    def name(self) -> str:
        """Return 'smart'."""
        return "smart"

    def resolve(self, left: Any, right: Any, base: Any = None) -> Any:
        """
        Intelligently resolve a conflict between two values.

        Args:
            left: The left/source value.
            right: The right/target value.
            base: The base value (for three-way merge, if available).

        Returns:
            The intelligently resolved value.
        """
        # If values are the same, no conflict
        if left == right:
            return copy.deepcopy(left)

        # Handle None values
        if left is None:
            return copy.deepcopy(right)
        if right is None:
            return copy.deepcopy(left)

        # If we have a base, use three-way merge logic
        if base is not None:
            left_changed = left != base
            right_changed = right != base

            if left_changed and right_changed:
                # Both sides changed - need to reconcile
                return self._reconcile(left, right, base)
            elif left_changed:
                # Only left changed
                return copy.deepcopy(left)
            elif right_changed:
                # Only right changed
                return copy.deepcopy(right)
            else:
                # Neither changed
                return copy.deepcopy(left)

        # No base - use two-way smart merge
        return self._reconcile(left, right, None)

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

    def _reconcile(self, left: Any, right: Any, base: Any = None) -> Any:
        """
        Reconcile two different values using smart heuristics.

        Args:
            left: The left value.
            right: The right value.
            base: The base value (if available).

        Returns:
            The reconciled value.
        """
        # Both are numbers - average them
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            result = (left + right) / 2
            if isinstance(left, int) and isinstance(right, int) and result == int(result):
                return int(result)
            return result

        # Both are strings - concatenate with separator
        if isinstance(left, str) and isinstance(right, str):
            return f"{left} {right}"

        # Both are booleans - AND logic
        if isinstance(left, bool) and isinstance(right, bool):
            return left and right

        # Both are lists - concatenate unique elements
        if isinstance(left, list) and isinstance(right, list):
            merged = copy.deepcopy(left)
            for item in right:
                if item not in merged:
                    merged.append(item)
            return merged

        # Both are dicts - merge recursively
        if isinstance(left, dict) and isinstance(right, dict):
            merged = copy.deepcopy(left)
            for key, value in right.items():
                if key in merged:
                    merged[key] = self.resolve(merged[key], value)
                else:
                    merged[key] = copy.deepcopy(value)
            return merged

        # Mixed types - prefer the more "specific" value
        type_priority = {
            dict: 6, list: 5, str: 4, float: 3, int: 2, bool: 1, type(None): 0
        }
        left_priority = type_priority.get(type(left), -1)
        right_priority = type_priority.get(type(right), -1)

        if left_priority >= right_priority:
            return copy.deepcopy(left)
        return copy.deepcopy(right)
