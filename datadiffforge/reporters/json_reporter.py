"""
JSON reporter for DataDiffForge.

Produces structured JSON output of diff results.
"""

import json
from typing import TYPE_CHECKING

from .base import ReporterInterface

if TYPE_CHECKING:
    from ..core.types import DiffResult


class JsonReporter(ReporterInterface):
    """
    Reporter that produces JSON formatted output.

    Serializes the entire DiffResult including all changes,
    statistics, and metadata as a JSON object.
    """

    @property
    def format_name(self) -> str:
        """Return 'json'."""
        return "json"

    def report(self, result: "DiffResult", **kwargs) -> str:
        """
        Format a DiffResult as a JSON string.

        Args:
            result: The diff result to format.
            **kwargs: Additional options:
                - indent: JSON indentation level (default: 2).
                - stat_only: If True, include only statistics.

        Returns:
            JSON formatted string.
        """
        indent = kwargs.get('indent', 2)
        stat_only = kwargs.get('stat_only', False)

        if stat_only:
            output = {
                "has_changes": result.has_changes,
                "total_changes": result.total_changes,
                "added_count": result.added_count,
                "removed_count": result.removed_count,
                "modified_count": result.modified_count,
                "type_changed_count": result.type_changed_count,
                "max_depth": result.max_depth,
                "stats_by_depth": {str(k): v for k, v in result.stats_by_depth.items()},
            }
        else:
            output = result.to_dict()

        return json.dumps(output, indent=indent, ensure_ascii=False, default=str)
