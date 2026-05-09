"""
Intelligent merge engine for DataDiffForge.

Provides merge functionality with configurable strategies, conflict detection,
and support for two-way and three-way merges.
"""

import copy
from typing import Any, Callable, Dict, List, Optional

from .differ import deep_diff, _safe_repr
from .path import Path, get_by_path, set_by_path
from .types import Change, Conflict, DiffOp, DiffResult


def merge(
    left: Any,
    right: Any,
    base: Optional[Any] = None,
    strategy: str = "smart",
    path: Optional[Path] = None,
    depth: int = 0,
    conflicts: Optional[List[Conflict]] = None,
    strategy_overrides: Optional[Dict[str, str]] = None,
) -> tuple:
    """
    Merge two values using the specified strategy.

    This is the main entry point for the merge engine. It supports both
    two-way merges (left + right) and three-way merges (base + left + right).

    Args:
        left: The left/source value.
        right: The right/target value.
        base: Optional base value for three-way merge.
        strategy: Default merge strategy name.
        path: Current path (for recursion).
        depth: Current nesting depth (for recursion).
        conflicts: List to collect conflicts (for recursion).
        strategy_overrides: Dict mapping path patterns to strategy names.

    Returns:
        A tuple of (merged_value, conflicts_list).
    """
    if path is None:
        path = Path.root()
    if conflicts is None:
        conflicts = []

    # Determine the effective strategy for this path
    effective_strategy = strategy
    if strategy_overrides:
        path_str = str(path)
        for pattern, strat in strategy_overrides.items():
            if path.matches_glob(Path.from_string(pattern)):
                effective_strategy = strat
                break

    # If values are identical, no merge needed
    if left == right:
        return copy.deepcopy(left), conflicts

    # For keep-both strategy with lists at the same level, concatenate directly
    if effective_strategy == "keep-both" and isinstance(left, list) and isinstance(right, list):
        merged_value = _apply_strategy(effective_strategy, path, left, right, base)
        return merged_value, conflicts

    # If both are dicts, merge recursively
    if isinstance(left, dict) and isinstance(right, dict):
        return _merge_dicts(left, right, base, effective_strategy, path, depth,
                            conflicts, strategy_overrides)

    # If both are lists, merge recursively
    if isinstance(left, list) and isinstance(right, list):
        return _merge_lists(left, right, base, effective_strategy, path, depth,
                            conflicts, strategy_overrides)

    # Values differ and are not both containers - this is a conflict
    # For three-way merge, check if only one side changed (not a real conflict)
    if base is not None and not isinstance(left, (dict, list)) and not isinstance(right, (dict, list)):
        left_changed = left != base
        right_changed = right != base
        if left_changed and not right_changed:
            return copy.deepcopy(left), conflicts
        if right_changed and not left_changed:
            return copy.deepcopy(right), conflicts

    merged_value = _apply_strategy(effective_strategy, path, left, right, base)
    conflict = Conflict(
        path=str(path),
        base_value=_safe_repr(base) if base is not None else None,
        left_value=_safe_repr(left),
        right_value=_safe_repr(right),
        strategy_used=effective_strategy,
        resolved_value=_safe_repr(merged_value),
    )
    conflicts.append(conflict)
    return merged_value, conflicts


def _merge_dicts(
    left: dict,
    right: dict,
    base: Optional[dict],
    strategy: str,
    path: Path,
    depth: int,
    conflicts: List[Conflict],
    strategy_overrides: Optional[Dict[str, str]],
) -> tuple:
    """
    Recursively merge two dictionaries.

    Args:
        left: The left dictionary.
        right: The right dictionary.
        base: Optional base dictionary for three-way merge.
        strategy: Default merge strategy.
        path: Current path.
        depth: Current depth.
        conflicts: List to collect conflicts.
        strategy_overrides: Strategy overrides by path.

    Returns:
        A tuple of (merged_dict, conflicts_list).
    """
    result = {}
    all_keys = set(left.keys()) | set(right.keys())

    for key in sorted(all_keys):
        child_path = path.key(key)
        in_left = key in left
        in_right = key in right
        in_base = key in base if base else None

        if in_left and in_right:
            # Key exists in both - recurse
            merged_val, conflicts = merge(
                left[key], right[key],
                base=base[key] if in_base else None,
                strategy=strategy,
                path=child_path,
                depth=depth + 1,
                conflicts=conflicts,
                strategy_overrides=strategy_overrides,
            )
            result[key] = merged_val
        elif in_left and not in_right:
            # Key only in left
            if base and in_base and base[key] == left[key]:
                # Left didn't change from base, right removed it - remove it
                pass
            else:
                # Left added or modified this key - keep it
                result[key] = copy.deepcopy(left[key])
        elif not in_left and in_right:
            # Key only in right
            if base and in_base and base[key] == right[key]:
                # Right didn't change from base, left removed it - remove it
                pass
            else:
                # Right added or modified this key - keep it
                result[key] = copy.deepcopy(right[key])

    return result, conflicts


def _merge_lists(
    left: list,
    right: list,
    base: Optional[list],
    strategy: str,
    path: Path,
    depth: int,
    conflicts: List[Conflict],
    strategy_overrides: Optional[Dict[str, str]],
) -> tuple:
    """
    Recursively merge two lists.

    Lists are merged positionally. If both lists have items at the same index,
    they are merged recursively. Extra items from either list are appended.

    Args:
        left: The left list.
        right: The right list.
        base: Optional base list for three-way merge.
        strategy: Default merge strategy.
        path: Current path.
        depth: Current depth.
        conflicts: List to collect conflicts.
        strategy_overrides: Strategy overrides by path.

    Returns:
        A tuple of (merged_list, conflicts_list).
    """
    result = []
    max_len = max(len(left), len(right))

    for i in range(max_len):
        child_path = path.index(i)
        in_left = i < len(left)
        in_right = i < len(right)
        in_base = base and i < len(base)

        if in_left and in_right:
            # Both have items at this index - recurse
            merged_val, conflicts = merge(
                left[i], right[i],
                base=base[i] if in_base else None,
                strategy=strategy,
                path=child_path,
                depth=depth + 1,
                conflicts=conflicts,
                strategy_overrides=strategy_overrides,
            )
            result.append(merged_val)
        elif in_left:
            result.append(copy.deepcopy(left[i]))
        elif in_right:
            result.append(copy.deepcopy(right[i]))

    return result, conflicts


def _apply_strategy(
    strategy: str,
    path: Path,
    left: Any,
    right: Any,
    base: Any = None,
) -> Any:
    """
    Apply a merge strategy to resolve a conflict between two values.

    Args:
        strategy: The strategy name to apply.
        path: The path where the conflict occurred.
        left: The left value.
        right: The right value.
        base: The base value (for three-way merge).

    Returns:
        The resolved value.
    """
    if strategy == "left-wins":
        return copy.deepcopy(left)
    elif strategy == "right-wins":
        return copy.deepcopy(right)
    elif strategy == "keep-both":
        # If both are lists, concatenate them
        if isinstance(left, list) and isinstance(right, list):
            return copy.deepcopy(left) + copy.deepcopy(right)
        # If both are dicts, merge them (right overrides left)
        if isinstance(left, dict) and isinstance(right, dict):
            merged = copy.deepcopy(left)
            merged.update(copy.deepcopy(right))
            return merged
        # For primitives, keep both as a list
        return [copy.deepcopy(left), copy.deepcopy(right)]
    elif strategy == "smart":
        return _smart_merge(left, right, base)
    else:
        # Default to left-wins for unknown strategies
        return copy.deepcopy(left)


def _smart_merge(left: Any, right: Any, base: Any = None) -> Any:
    """
    Apply intelligent merge heuristics to resolve a conflict.

    Smart merge rules:
    - Numeric values: average if both changed from base, otherwise take the changed one
    - Strings: concatenate with a separator if both changed from base
    - Booleans: use AND logic
    - Lists: concatenate unique elements
    - Dicts: merge recursively
    - Mixed types: prefer the non-None value, or the value that changed from base

    Args:
        left: The left value.
        right: The right value.
        base: The base value (for three-way merge).

    Returns:
        The intelligently merged value.
    """
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
            # Both changed - need to reconcile
            return _smart_reconcile(left, right, base)
        elif left_changed:
            return copy.deepcopy(left)
        elif right_changed:
            return copy.deepcopy(right)
        else:
            # Neither changed (shouldn't happen if we got here)
            return copy.deepcopy(left)

    # No base - use two-way smart merge
    return _smart_reconcile(left, right, None)


def _smart_reconcile(left: Any, right: Any, base: Any = None) -> Any:
    """
    Reconcile two different values using smart heuristics.

    Args:
        left: The left value.
        right: The right value.
        base: The base value (if available).

    Returns:
        The reconciled value.
    """
    # Both are booleans - AND logic (check before int since bool is subclass of int)
    if isinstance(left, bool) and isinstance(right, bool):
        return left and right

    # Both are numbers - average them
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        result = (left + right) / 2
        # Return int if both inputs are int and result is whole number
        if isinstance(left, int) and isinstance(right, int) and result == int(result):
            return int(result)
        return result

    # Both are strings - concatenate with separator
    if isinstance(left, str) and isinstance(right, str):
        return f"{left} {right}"

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
                merged[key], _ = _smart_reconcile_both(merged[key], value)
            else:
                merged[key] = copy.deepcopy(value)
        return merged

    # Mixed types - prefer the more "specific" value
    # Priority: dict > list > str > number > bool > None
    type_priority = {dict: 6, list: 5, str: 4, float: 3, int: 2, bool: 1, type(None): 0}
    left_priority = type_priority.get(type(left), -1)
    right_priority = type_priority.get(type(right), -1)

    if left_priority >= right_priority:
        return copy.deepcopy(left)
    return copy.deepcopy(right)


def _smart_reconcile_both(left: Any, right: Any) -> tuple:
    """
    Helper for smart reconciliation that returns (value, conflicts).

    Args:
        left: The left value.
        right: The right value.

    Returns:
        A tuple of (merged_value, empty_conflicts_list).
    """
    return _smart_reconcile(left, right), []


def merge_with_report(
    left: Any,
    right: Any,
    base: Optional[Any] = None,
    strategy: str = "smart",
    strategy_overrides: Optional[Dict[str, str]] = None,
    left_label: str = "left",
    right_label: str = "right",
) -> Dict[str, Any]:
    """
    Perform a merge and generate a detailed merge report.

    Args:
        left: The left/source value.
        right: The right/target value.
        base: Optional base value for three-way merge.
        strategy: Default merge strategy name.
        strategy_overrides: Dict mapping path patterns to strategy names.
        left_label: Label for the left data source.
        right_label: Label for the right data source.

    Returns:
        A dictionary containing:
        - merged: The merged result
        - conflicts: List of Conflict objects
        - conflict_count: Number of conflicts
        - strategy: Strategy used
    """
    merged_value, conflicts = merge(
        left=left,
        right=right,
        base=base,
        strategy=strategy,
        strategy_overrides=strategy_overrides,
    )

    return {
        "merged": merged_value,
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
        "strategy": strategy,
        "left_label": left_label,
        "right_label": right_label,
    }
