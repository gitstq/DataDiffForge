"""
JSONPath-like path tracking for nested structures.

Provides utilities for building and manipulating path strings that
identify locations within nested dict/list structures, similar to
JSONPath or XPath notation.
"""

from typing import Any, List, Union


class Path:
    """
    Represents a JSONPath-like path for tracking locations in nested data.

    Paths use the following notation:
    - Root: "$"
    - Dict key: "$.key"
    - List index: "$[0]"
    - Nested: "$.users[0].name"

    Examples:
        >>> p = Path.root()
        >>> p.key("users").index(0).key("name")
        Path('$.users[0].name')
        >>> str(p)
        '$.users[0].name'
    """

    def __init__(self, segments: List[str] = None) -> None:
        """Initialize a Path with optional pre-existing segments."""
        self._segments: List[str] = segments or []

    @classmethod
    def root(cls) -> "Path":
        """Create a new root path (represented as '$')."""
        return cls()

    @classmethod
    def from_string(cls, path_str: str) -> "Path":
        """
        Parse a JSONPath-like string into a Path object.

        Args:
            path_str: A JSONPath string like "$.users[0].name"

        Returns:
            A Path object representing the same location.
        """
        if not path_str or path_str == "$":
            return cls.root()

        segments: List[str] = []
        # Remove leading "$" if present
        remaining = path_str
        if remaining.startswith("$"):
            remaining = remaining[1:]

        # Remove leading dot if present
        if remaining.startswith("."):
            remaining = remaining[1:]

        # Parse the remaining path
        i = 0
        while i < len(remaining):
            if remaining[i] == ".":
                i += 1
                # Read key name
                j = i
                while j < len(remaining) and remaining[j] not in ".[":
                    j += 1
                if j > i:
                    segments.append(("key", remaining[i:j]))
                i = j
            elif remaining[i] == "[":
                # Read array index
                j = i + 1
                while j < len(remaining) and remaining[j] != "]":
                    j += 1
                index_str = remaining[i + 1:j]
                segments.append(("index", int(index_str)))
                i = j + 1
                # Skip trailing dot
                if i < len(remaining) and remaining[i] == ".":
                    i += 1
            else:
                # Read key name
                j = i
                while j < len(remaining) and remaining[j] not in ".[":
                    j += 1
                if j > i:
                    segments.append(("key", remaining[i:j]))
                i = j

        path = cls()
        path._segments = segments
        return path

    def key(self, name: str) -> "Path":
        """
        Append a dictionary key to this path.

        Args:
            name: The key name to append.

        Returns:
            A new Path with the key appended.
        """
        new_segments = self._segments.copy()
        new_segments.append(("key", name))
        return Path(new_segments)

    def index(self, idx: int) -> "Path":
        """
        Append a list index to this path.

        Args:
            idx: The index to append.

        Returns:
            A new Path with the index appended.
        """
        new_segments = self._segments.copy()
        new_segments.append(("index", idx))
        return Path(new_segments)

    def parent(self) -> "Path":
        """
        Return a new Path representing the parent of this path.

        Returns:
            A new Path with the last segment removed, or root if already at root.
        """
        if not self._segments:
            return Path.root()
        return Path(self._segments[:-1])

    @property
    def depth(self) -> int:
        """Return the depth (number of segments) of this path."""
        return len(self._segments)

    def __str__(self) -> str:
        """Convert this path to a JSONPath-like string."""
        if not self._segments:
            return "$"

        parts: List[str] = []
        for seg_type, seg_value in self._segments:
            if seg_type == "key":
                # Use bracket notation for keys with special characters
                if isinstance(seg_value, str) and all(
                    c.isalnum() or c == "_" or c == "-" for c in seg_value
                ):
                    parts.append(f".{seg_value}")
                else:
                    parts.append(f"['{seg_value}']")
            elif seg_type == "index":
                parts.append(f"[{seg_value}]")

        return "$" + "".join(parts)

    def __repr__(self) -> str:
        return f"Path('{self}')"

    def __eq__(self, other: object) -> bool:
        """Check equality with another Path or string."""
        if isinstance(other, Path):
            return self._segments == other._segments
        if isinstance(other, str):
            return str(self) == other
        return NotImplemented

    def __hash__(self) -> int:
        """Return hash for this path."""
        return hash(str(self))

    def __len__(self) -> int:
        """Return the number of segments in this path."""
        return len(self._segments)

    def matches_glob(self, pattern: str) -> bool:
        """
        Check if this path matches a glob-like pattern.

        Supports:
        - "*" to match any single key/index segment
        - "**" to match any number of segments (zero or more)

        Args:
            pattern: A glob pattern like "$.users.*.name" or "$.users.**"

        Returns:
            True if this path matches the pattern.
        """
        pattern_path = Path.from_string(pattern)
        return self._matches_segments(self._segments, pattern_path._segments)

    @staticmethod
    def _matches_segments(segments: List[tuple], pattern_segments: List[tuple]) -> bool:
        """
        Recursively match path segments against pattern segments.

        Args:
            segments: The actual path segments.
            pattern_segments: The pattern segments to match against.

        Returns:
            True if all segments match the pattern.
        """
        if not pattern_segments:
            return not segments

        pat_type, pat_value = pattern_segments[0]

        # Handle double-star wildcard (matches zero or more segments)
        if pat_type == "key" and pat_value == "**":
            # Try matching zero segments (skip the **)
            if Path._matches_segments(segments, pattern_segments[1:]):
                return True
            # Try matching one or more segments
            if segments:
                return Path._matches_segments(segments[1:], pattern_segments)
            return False

        if not segments:
            return False

        seg_type, seg_value = segments[0]

        # Handle single-star wildcard (matches any single segment)
        if pat_type == "key" and pat_value == "*":
            return Path._matches_segments(segments[1:], pattern_segments[1:])

        # Exact match required
        if seg_type == pat_type and seg_value == pat_value:
            return Path._matches_segments(segments[1:], pattern_segments[1:])

        return False


def get_by_path(data: Any, path: Path) -> Any:
    """
    Retrieve a value from nested data using a Path.

    Args:
        data: The nested data structure (dict, list, or primitive).
        path: The Path identifying the location to retrieve.

    Returns:
        The value at the specified path.

    Raises:
        KeyError: If a dictionary key is not found.
        IndexError: If a list index is out of range.
        TypeError: If the path navigates through a non-container type.
    """
    current = data
    for seg_type, seg_value in path._segments:
        if seg_type == "key":
            if not isinstance(current, dict):
                raise TypeError(
                    f"Expected dict at path segment '{seg_value}', got {type(current).__name__}"
                )
            current = current[seg_value]
        elif seg_type == "index":
            if not isinstance(current, list):
                raise TypeError(
                    f"Expected list at path segment [{seg_value}], got {type(current).__name__}"
                )
            current = current[seg_value]
    return current


def set_by_path(data: Any, path: Path, value: Any) -> None:
    """
    Set a value in nested data using a Path.

    Args:
        data: The nested data structure (must be mutable).
        path: The Path identifying the location to set.
        value: The value to set.

    Raises:
        KeyError: If a dictionary key is not found.
        IndexError: If a list index is out of range.
        TypeError: If the path navigates through a non-container type.
    """
    if not path._segments:
        raise ValueError("Cannot set value at root path")

    # Navigate to the parent, then set the final key/index
    parent = data
    for seg_type, seg_value in path._segments[:-1]:
        if seg_type == "key":
            parent = parent[seg_value]
        elif seg_type == "index":
            parent = parent[seg_value]

    final_type, final_value = path._segments[-1]
    if final_type == "key":
        parent[final_value] = value
    elif final_type == "index":
        parent[final_value] = value
