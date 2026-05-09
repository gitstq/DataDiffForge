"""
Core types for DataDiffForge.

Defines the fundamental data structures used throughout the diff and merge engine:
- DiffOp: Enumeration of diff operation types
- Change: Represents a single detected change
- Conflict: Represents a merge conflict
- DiffResult: Aggregates all changes and statistics from a diff operation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class DiffOp(Enum):
    """Enumeration of possible diff operation types."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    TYPE_CHANGED = "type_changed"

    def __str__(self) -> str:
        return self.value


@dataclass
class Change:
    """
    Represents a single change detected during a diff operation.

    Attributes:
        op: The type of change operation.
        path: JSONPath-like string indicating where the change occurred.
        old_value: The original value (None for ADDED operations).
        new_value: The new value (None for REMOVED operations).
        old_type: The type name of the original value.
        new_type: The type name of the new value.
        depth: The nesting depth at which this change was detected.
    """
    op: DiffOp
    path: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    old_type: Optional[str] = None
    new_type: Optional[str] = None
    depth: int = 0

    def __str__(self) -> str:
        """Return a human-readable string representation of this change."""
        if self.op == DiffOp.ADDED:
            return f"+ {self.path}: {self.new_value!r}"
        elif self.op == DiffOp.REMOVED:
            return f"- {self.path}: {self.old_value!r}"
        elif self.op == DiffOp.TYPE_CHANGED:
            return f"~ {self.path}: {self.old_type} -> {self.new_type} ({self.old_value!r} -> {self.new_value!r})"
        else:
            return f"~ {self.path}: {self.old_value!r} -> {self.new_value!r}"


@dataclass
class Conflict:
    """
    Represents a merge conflict where both sides modified the same path.

    Attributes:
        path: JSONPath-like string indicating where the conflict occurred.
        base_value: The value in the base version (if available).
        left_value: The value from the left/source side.
        right_value: The value from the right/target side.
        strategy_used: The merge strategy that was applied.
        resolved_value: The final resolved value after applying the strategy.
    """
    path: str
    base_value: Optional[Any] = None
    left_value: Optional[Any] = None
    right_value: Optional[Any] = None
    strategy_used: str = "smart"
    resolved_value: Optional[Any] = None

    def __str__(self) -> str:
        """Return a human-readable string representation of this conflict."""
        return (
            f"Conflict at {self.path}: "
            f"left={self.left_value!r}, right={self.right_value!r} "
            f"-> resolved={self.resolved_value!r} (strategy: {self.strategy_used})"
        )


@dataclass
class DiffResult:
    """
    Aggregates all changes and statistics from a diff operation.

    Attributes:
        changes: List of all detected changes.
        left_label: Label for the left/source data.
        right_label: Label for the right/target data.
        total_changes: Total number of changes detected.
        added_count: Number of additions.
        removed_count: Number of removals.
        modified_count: Number of modifications.
        type_changed_count: Number of type changes.
        max_depth: Maximum nesting depth encountered.
        stats_by_depth: Dictionary mapping depth levels to change counts.
    """
    changes: List[Change] = field(default_factory=list)
    left_label: str = "left"
    right_label: str = "right"
    total_changes: int = 0
    added_count: int = 0
    removed_count: int = 0
    modified_count: int = 0
    type_changed_count: int = 0
    max_depth: int = 0
    stats_by_depth: Dict[int, int] = field(default_factory=dict)

    def add_change(self, change: Change) -> None:
        """Add a change and update all statistics."""
        self.changes.append(change)
        self.total_changes += 1

        # Update operation-specific counters
        if change.op == DiffOp.ADDED:
            self.added_count += 1
        elif change.op == DiffOp.REMOVED:
            self.removed_count += 1
        elif change.op == DiffOp.MODIFIED:
            self.modified_count += 1
        elif change.op == DiffOp.TYPE_CHANGED:
            self.type_changed_count += 1

        # Update depth statistics
        depth = change.depth
        self.stats_by_depth[depth] = self.stats_by_depth.get(depth, 0) + 1
        if depth > self.max_depth:
            self.max_depth = depth

    @property
    def has_changes(self) -> bool:
        """Return True if any changes were detected."""
        return self.total_changes > 0

    def summary(self) -> str:
        """Return a human-readable summary of the diff result."""
        if not self.has_changes:
            return "No differences found."
        parts = [
            f"Total changes: {self.total_changes}",
            f"  Added: {self.added_count}",
            f"  Removed: {self.removed_count}",
            f"  Modified: {self.modified_count}",
            f"  Type changed: {self.type_changed_count}",
            f"  Max depth: {self.max_depth}",
        ]
        return "\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the diff result to a dictionary."""
        return {
            "left_label": self.left_label,
            "right_label": self.right_label,
            "total_changes": self.total_changes,
            "added_count": self.added_count,
            "removed_count": self.removed_count,
            "modified_count": self.modified_count,
            "type_changed_count": self.type_changed_count,
            "max_depth": self.max_depth,
            "stats_by_depth": {str(k): v for k, v in self.stats_by_depth.items()},
            "changes": [
                {
                    "op": str(c.op),
                    "path": c.path,
                    "old_value": c.old_value,
                    "new_value": c.new_value,
                    "old_type": c.old_type,
                    "new_type": c.new_type,
                    "depth": c.depth,
                }
                for c in self.changes
            ],
        }
