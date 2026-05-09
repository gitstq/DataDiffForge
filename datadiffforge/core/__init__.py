"""
Core package for DataDiffForge.

Re-exports the main types and functions from the core submodules.
"""

from .types import Change, Conflict, DiffOp, DiffResult
from .differ import diff, deep_diff
from .merger import merge, merge_with_report
from .path import Path, get_by_path, set_by_path

__all__ = [
    "Change",
    "Conflict",
    "DiffOp",
    "DiffResult",
    "diff",
    "deep_diff",
    "merge",
    "merge_with_report",
    "Path",
    "get_by_path",
    "set_by_path",
]
