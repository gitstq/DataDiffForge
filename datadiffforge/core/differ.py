"""
Core diff engine for DataDiffForge.

Provides recursive deep comparison of nested data structures (dicts, lists, primitives),
tracking JSONPath for each change and supporting various filtering options.
"""

from typing import Any, Callable, List, Optional, Set, Tuple

from .path import Path
from .types import Change, DiffOp, DiffResult


def deep_diff(
    left: Any,
    right: Any,
    path: Optional[Path] = None,
    depth: int = 0,
    max_depth: Optional[int] = None,
    ignore_paths: Optional[List[str]] = None,
    ignore_set: Optional[Set[str]] = None,
    key_fn: Optional[Callable[[str], str]] = None,
    result: Optional[DiffResult] = None,
    left_label: str = "left",
    right_label: str = "right",
) -> DiffResult:
    """
    Recursively compare two values and record all differences.

    This is the core diff engine that handles nested dicts, lists, and primitives.
    It tracks the JSONPath for each change and supports filtering by path patterns
    and limiting comparison depth.

    Args:
        left: The left/source value to compare.
        right: The right/target value to compare.
        path: Current path in the data structure (for recursion).
        depth: Current nesting depth (for recursion).
        max_depth: Maximum depth to compare (None for unlimited).
        ignore_paths: List of glob patterns for paths to ignore.
        ignore_set: Pre-computed set of ignored path strings (internal use).
        key_fn: Optional function to transform keys before comparison.
        result: Existing DiffResult to append to (for recursion).
        left_label: Label for the left data source.
        right_label: Label for the right data source.

    Returns:
        A DiffResult containing all detected changes and statistics.
    """
    if path is None:
        path = Path.root()
    if result is None:
        result = DiffResult(left_label=left_label, right_label=right_label)

    # Pre-compute ignore set on first call
    if ignore_set is None and ignore_paths:
        ignore_set = set(ignore_paths)

    # Check if this path should be ignored
    if ignore_set:
        path_str = str(path)
        for pattern in ignore_paths:
            if path.matches_glob(pattern):
                return result

    # Check depth limit
    if max_depth is not None and depth > max_depth:
        return result

    # Normalize keys if a key function is provided
    left_normalized = _normalize_keys(left, key_fn) if key_fn and isinstance(left, dict) else left
    right_normalized = _normalize_keys(right, key_fn) if key_fn and isinstance(right, dict) else right

    # Compute type names for reporting
    left_type = type(left_normalized).__name__
    right_type = type(right_normalized).__name__

    # Handle None values before type comparison
    # None vs non-None is treated as ADDED/REMOVED, not TYPE_CHANGED
    if left_normalized is None and right_normalized is None:
        return result
    if left_normalized is None or right_normalized is None:
        result.add_change(Change(
            op=DiffOp.ADDED if left_normalized is None else DiffOp.REMOVED,
            path=str(path),
            old_value=None if left_normalized is None else _safe_repr(left_normalized),
            new_value=None if right_normalized is None else _safe_repr(right_normalized),
            old_type=left_type,
            new_type=right_type,
            depth=depth,
        ))
        return result

    # Type comparison
    if left_type != right_type:
        # Both are container types of different kinds
        if isinstance(left_normalized, dict) and isinstance(right_normalized, dict):
            pass  # Both dicts, compare normally
        elif isinstance(left_normalized, list) and isinstance(right_normalized, list):
            pass  # Both lists, compare normally
        else:
            result.add_change(Change(
                op=DiffOp.TYPE_CHANGED,
                path=str(path),
                old_value=_safe_repr(left),
                new_value=_safe_repr(right),
                old_type=left_type,
                new_type=right_type,
                depth=depth,
            ))
            return result

    # Dict comparison
    if isinstance(left_normalized, dict) and isinstance(right_normalized, dict):
        _diff_dicts(left_normalized, right_normalized, path, depth, max_depth,
                     ignore_paths, ignore_set, key_fn, result)
        return result

    # List comparison
    if isinstance(left_normalized, list) and isinstance(right_normalized, list):
        _diff_lists(left_normalized, right_normalized, path, depth, max_depth,
                     ignore_paths, ignore_set, key_fn, result)
        return result

    # Primitive comparison
    if left_normalized != right_normalized:
        result.add_change(Change(
            op=DiffOp.MODIFIED,
            path=str(path),
            old_value=_safe_repr(left_normalized),
            new_value=_safe_repr(right_normalized),
            old_type=left_type,
            new_type=right_type,
            depth=depth,
        ))

    return result


def _diff_dicts(
    left: dict,
    right: dict,
    path: Path,
    depth: int,
    max_depth: Optional[int],
    ignore_paths: Optional[List[str]],
    ignore_set: Optional[Set[str]],
    key_fn: Optional[Callable[[str], str]],
    result: DiffResult,
) -> None:
    """
    Compare two dictionaries and record differences.

    Args:
        left: The left dictionary.
        right: The right dictionary.
        path: Current path in the data structure.
        depth: Current nesting depth.
        max_depth: Maximum depth to compare.
        ignore_paths: Paths to ignore.
        ignore_set: Pre-computed ignore set.
        key_fn: Key normalization function.
        result: DiffResult to append changes to.
    """
    all_keys = set(left.keys()) | set(right.keys())

    for key in sorted(all_keys):
        child_path = path.key(key)

        # Check if this path should be ignored
        if ignore_paths:
            should_ignore = False
            for pattern in ignore_paths:
                if child_path.matches_glob(pattern):
                    should_ignore = True
                    break
            if should_ignore:
                continue

        if key not in left:
            # Key was added
            result.add_change(Change(
                op=DiffOp.ADDED,
                path=str(child_path),
                new_value=_safe_repr(right[key]),
                new_type=type(right[key]).__name__,
                depth=depth,
            ))
        elif key not in right:
            # Key was removed
            result.add_change(Change(
                op=DiffOp.REMOVED,
                path=str(child_path),
                old_value=_safe_repr(left[key]),
                old_type=type(left[key]).__name__,
                depth=depth,
            ))
        else:
            # Key exists in both, recurse
            deep_diff(
                left[key], right[key],
                path=child_path,
                depth=depth + 1,
                max_depth=max_depth,
                ignore_paths=ignore_paths,
                ignore_set=ignore_set,
                key_fn=key_fn,
                result=result,
            )


def _diff_lists(
    left: list,
    right: list,
    path: Path,
    depth: int,
    max_depth: Optional[int],
    ignore_paths: Optional[List[str]],
    ignore_set: Optional[Set[str]],
    key_fn: Optional[Callable[[str], str]],
    result: DiffResult,
) -> None:
    """
    Compare two lists and record differences.

    Lists are compared positionally (order-sensitive). Items at the same
    index are compared recursively.

    Args:
        left: The left list.
        right: The right list.
        path: Current path in the data structure.
        depth: Current nesting depth.
        max_depth: Maximum depth to compare.
        ignore_paths: Paths to ignore.
        ignore_set: Pre-computed ignore set.
        key_fn: Key normalization function.
        result: DiffResult to append changes to.
    """
    max_len = max(len(left), len(right))

    for i in range(max_len):
        child_path = path.index(i)

        # Check if this path should be ignored
        if ignore_paths:
            should_ignore = False
            for pattern in ignore_paths:
                if child_path.matches_glob(pattern):
                    should_ignore = True
                    break
            if should_ignore:
                continue

        if i >= len(left):
            # Item was added
            result.add_change(Change(
                op=DiffOp.ADDED,
                path=str(child_path),
                new_value=_safe_repr(right[i]),
                new_type=type(right[i]).__name__,
                depth=depth,
            ))
        elif i >= len(right):
            # Item was removed
            result.add_change(Change(
                op=DiffOp.REMOVED,
                path=str(child_path),
                old_value=_safe_repr(left[i]),
                old_type=type(left[i]).__name__,
                depth=depth,
            ))
        else:
            # Both have items at this index, recurse
            deep_diff(
                left[i], right[i],
                path=child_path,
                depth=depth + 1,
                max_depth=max_depth,
                ignore_paths=ignore_paths,
                ignore_set=ignore_set,
                key_fn=key_fn,
                result=result,
            )


def _normalize_keys(data: Any, key_fn: Callable[[str], str]) -> Any:
    """
    Recursively normalize dictionary keys using the provided function.

    Args:
        data: The data structure to normalize.
        key_fn: Function to transform keys.

    Returns:
        A new data structure with normalized keys.
    """
    if isinstance(data, dict):
        return {key_fn(k): _normalize_keys(v, key_fn) for k, v in data.items()}
    elif isinstance(data, list):
        return [_normalize_keys(item, key_fn) for item in data]
    return data


def _safe_repr(value: Any) -> Any:
    """
    Create a safe representation of a value for storage in Change objects.

    For simple types, returns the value directly. For complex types,
    returns a string representation to avoid issues with serialization.

    Args:
        value: The value to represent.

    Returns:
        A safe representation of the value.
    """
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (dict, list)):
        # Return a truncated representation for complex types
        s = repr(value)
        if len(s) > 200:
            return s[:200] + "..."
        return s
    return repr(value)


def diff(
    left: Any,
    right: Any,
    left_label: str = "left",
    right_label: str = "right",
    ignore_paths: Optional[List[str]] = None,
    max_depth: Optional[int] = None,
    key_fn: Optional[Callable[[str], str]] = None,
) -> DiffResult:
    """
    High-level API for computing a deep diff between two values.

    This is the main entry point for the diff engine. It compares two values
    recursively and returns a structured result with all detected changes.

    Args:
        left: The left/source value to compare.
        right: The right/target value to compare.
        left_label: Label for the left data source.
        right_label: Label for the right data source.
        ignore_paths: List of glob patterns for paths to ignore.
        max_depth: Maximum depth to compare (None for unlimited).
        key_fn: Optional function to transform keys before comparison.

    Returns:
        A DiffResult containing all detected changes and statistics.

    Example:
        >>> result = diff({"a": 1}, {"a": 2, "b": 3})
        >>> result.total_changes
        2
        >>> result.changes[0].op
        <DiffOp.MODIFIED: 'modified'>
    """
    return deep_diff(
        left=left,
        right=right,
        path=Path.root(),
        depth=0,
        max_depth=max_depth,
        ignore_paths=ignore_paths,
        key_fn=key_fn,
        left_label=left_label,
        right_label=right_label,
    )
