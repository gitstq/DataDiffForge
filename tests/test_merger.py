"""
Comprehensive tests for the merge engine.

Tests cover:
- Two-way merge with all strategies
- Three-way merge
- Conflict detection
- Nested structure merging
- List merging
- Edge cases
"""

import unittest

from datadiffforge.core.merger import merge, merge_with_report, _apply_strategy
from datadiffforge.core.types import Conflict


class TestMergeBasic(unittest.TestCase):
    """Tests for basic merge functionality."""

    def test_identical_values(self):
        """Merging identical values should return the value unchanged."""
        merged, conflicts = merge({"a": 1}, {"a": 1})
        self.assertEqual(merged, {"a": 1})
        self.assertEqual(len(conflicts), 0)

    def test_left_wins_strategy(self):
        """Left-wins strategy should prefer left values."""
        merged, conflicts = merge({"a": 1}, {"a": 2}, strategy="left-wins")
        self.assertEqual(merged, {"a": 1})
        self.assertEqual(len(conflicts), 1)

    def test_right_wins_strategy(self):
        """Right-wins strategy should prefer right values."""
        merged, conflicts = merge({"a": 1}, {"a": 2}, strategy="right-wins")
        self.assertEqual(merged, {"a": 2})
        self.assertEqual(len(conflicts), 1)

    def test_keep_both_strategy_primitives(self):
        """Keep-both strategy should return both values as a list for primitives."""
        merged, conflicts = merge({"a": 1}, {"a": 2}, strategy="keep-both")
        self.assertEqual(merged, {"a": [1, 2]})
        self.assertEqual(len(conflicts), 1)

    def test_keep_both_strategy_lists(self):
        """Keep-both strategy should concatenate lists."""
        merged, conflicts = merge({"a": [1, 2]}, {"a": [3, 4]}, strategy="keep-both")
        self.assertEqual(merged, {"a": [1, 2, 3, 4]})

    def test_keep_both_strategy_dicts(self):
        """Keep-both strategy should merge dicts."""
        merged, conflicts = merge({"a": {"x": 1}}, {"a": {"y": 2}}, strategy="keep-both")
        self.assertEqual(merged, {"a": {"x": 1, "y": 2}})

    def test_smart_strategy_numbers(self):
        """Smart strategy should average numbers."""
        merged, conflicts = merge({"a": 10}, {"a": 20}, strategy="smart")
        self.assertEqual(merged, {"a": 15})

    def test_smart_strategy_strings(self):
        """Smart strategy should concatenate strings."""
        merged, conflicts = merge({"a": "hello"}, {"a": "world"}, strategy="smart")
        self.assertEqual(merged, {"a": "hello world"})

    def test_smart_strategy_booleans(self):
        """Smart strategy should AND booleans."""
        merged, conflicts = merge({"a": True}, {"a": False}, strategy="smart")
        self.assertEqual(merged, {"a": False})

    def test_smart_strategy_lists(self):
        """Smart strategy should merge lists positionally (averaging numbers)."""
        merged, conflicts = merge({"a": [1, 2]}, {"a": [2, 3]}, strategy="smart")
        # Lists are merged positionally: index 0 averages 1 and 2, index 1 averages 2 and 3
        self.assertEqual(merged, {"a": [1.5, 2.5]})


class TestThreeWayMerge(unittest.TestCase):
    """Tests for three-way merge functionality."""

    def test_both_unchanged(self):
        """If both sides match base, no changes needed."""
        base = {"a": 1, "b": 2}
        left = {"a": 1, "b": 2}
        right = {"a": 1, "b": 2}
        merged, conflicts = merge(left, right, base=base, strategy="smart")
        self.assertEqual(merged, {"a": 1, "b": 2})
        self.assertEqual(len(conflicts), 0)

    def test_only_left_changed(self):
        """If only left changed, left value should be used."""
        base = {"a": 1}
        left = {"a": 99}
        right = {"a": 1}
        merged, conflicts = merge(left, right, base=base, strategy="smart")
        self.assertEqual(merged, {"a": 99})
        self.assertEqual(len(conflicts), 0)

    def test_only_right_changed(self):
        """If only right changed, right value should be used."""
        base = {"a": 1}
        left = {"a": 1}
        right = {"a": 99}
        merged, conflicts = merge(left, right, base=base, strategy="smart")
        self.assertEqual(merged, {"a": 99})
        self.assertEqual(len(conflicts), 0)

    def test_both_changed_same(self):
        """If both changed to the same value, use that value."""
        base = {"a": 1}
        left = {"a": 99}
        right = {"a": 99}
        merged, conflicts = merge(left, right, base=base, strategy="smart")
        self.assertEqual(merged, {"a": 99})
        self.assertEqual(len(conflicts), 0)

    def test_both_changed_differently(self):
        """If both changed differently, should be a conflict."""
        base = {"a": 1}
        left = {"a": 10}
        right = {"a": 20}
        merged, conflicts = merge(left, right, base=base, strategy="smart")
        self.assertEqual(merged, {"a": 15})  # Smart averages
        self.assertEqual(len(conflicts), 1)

    def test_left_added_right_unchanged(self):
        """If left added a key and right didn't change, keep the addition."""
        base = {"a": 1}
        left = {"a": 1, "b": 2}
        right = {"a": 1}
        merged, conflicts = merge(left, right, base=base, strategy="smart")
        self.assertEqual(merged, {"a": 1, "b": 2})

    def test_right_added_left_unchanged(self):
        """If right added a key and left didn't change, keep the addition."""
        base = {"a": 1}
        left = {"a": 1}
        right = {"a": 1, "b": 2}
        merged, conflicts = merge(left, right, base=base, strategy="smart")
        self.assertEqual(merged, {"a": 1, "b": 2})

    def test_left_removed_right_unchanged(self):
        """If left removed a key and right didn't change, remove it."""
        base = {"a": 1, "b": 2}
        left = {"a": 1}
        right = {"a": 1, "b": 2}
        merged, conflicts = merge(left, right, base=base, strategy="smart")
        self.assertEqual(merged, {"a": 1})

    def test_right_removed_left_unchanged(self):
        """If right removed a key and left didn't change, remove it."""
        base = {"a": 1, "b": 2}
        left = {"a": 1, "b": 2}
        right = {"a": 1}
        merged, conflicts = merge(left, right, base=base, strategy="smart")
        self.assertEqual(merged, {"a": 1})


class TestMergeNestedStructures(unittest.TestCase):
    """Tests for merging nested structures."""

    def test_nested_dict_merge(self):
        """Nested dicts should be merged recursively."""
        left = {"a": {"x": 1, "y": 2}}
        right = {"a": {"y": 99, "z": 3}}
        merged, conflicts = merge(left, right, strategy="smart")
        self.assertEqual(merged["a"]["x"], 1)    # Only in left
        self.assertEqual(merged["a"]["y"], 50.5)  # Smart averages numbers
        self.assertEqual(merged["a"]["z"], 3)    # Only in right

    def test_nested_list_merge(self):
        """Nested lists should be merged positionally."""
        left = {"items": [1, 2, 3]}
        right = {"items": [1, 99, 3]}
        merged, conflicts = merge(left, right, strategy="smart")
        self.assertEqual(merged["items"], [1, 50.5, 3])  # Smart averages 2 and 99

    def test_deeply_nested_merge(self):
        """Deeply nested structures should be merged correctly."""
        left = {"a": {"b": {"c": {"d": 10}}}}
        right = {"a": {"b": {"c": {"d": 20}}}}
        merged, conflicts = merge(left, right, strategy="smart")
        self.assertEqual(merged["a"]["b"]["c"]["d"], 15)


class TestMergeWithReport(unittest.TestCase):
    """Tests for the merge_with_report function."""

    def test_report_structure(self):
        """merge_with_report should return a dict with expected keys."""
        report = merge_with_report({"a": 1}, {"a": 2}, strategy="left-wins")
        self.assertIn("merged", report)
        self.assertIn("conflicts", report)
        self.assertIn("conflict_count", report)
        self.assertIn("strategy", report)

    def test_report_conflict_count(self):
        """Conflict count should match actual conflicts."""
        report = merge_with_report({"a": 1}, {"a": 2}, strategy="left-wins")
        self.assertEqual(report["conflict_count"], 1)

    def test_report_no_conflicts(self):
        """Identical values should produce no conflicts."""
        report = merge_with_report({"a": 1}, {"a": 1})
        self.assertEqual(report["conflict_count"], 0)

    def test_report_labels(self):
        """Labels should be stored in the report."""
        report = merge_with_report(
            {"a": 1}, {"a": 2},
            left_label="file1", right_label="file2"
        )
        self.assertEqual(report["left_label"], "file1")
        self.assertEqual(report["right_label"], "file2")


class TestMergeEdgeCases(unittest.TestCase):
    """Tests for merge edge cases."""

    def test_empty_dicts(self):
        """Merging empty dicts should produce empty dict."""
        merged, conflicts = merge({}, {})
        self.assertEqual(merged, {})
        self.assertEqual(len(conflicts), 0)

    def test_empty_vs_nonempty(self):
        """Merging empty with non-empty should include all keys."""
        merged, conflicts = merge({}, {"a": 1, "b": 2})
        self.assertEqual(merged, {"a": 1, "b": 2})
        self.assertEqual(len(conflicts), 0)

    def test_none_values(self):
        """None values should be handled correctly."""
        merged, conflicts = merge({"a": None}, {"a": "value"}, strategy="smart")
        self.assertEqual(merged, {"a": "value"})

    def test_mixed_types(self):
        """Smart merge with mixed types should prefer more specific type."""
        merged, conflicts = merge({"a": [1, 2]}, {"a": "string"}, strategy="smart")
        # List has higher priority than string
        self.assertEqual(merged, {"a": [1, 2]})

    def test_list_length_difference(self):
        """Lists of different lengths should be merged correctly."""
        left = {"items": [1, 2]}
        right = {"items": [1, 2, 3, 4]}
        merged, conflicts = merge(left, right, strategy="smart")
        self.assertEqual(len(merged["items"]), 4)


if __name__ == "__main__":
    unittest.main()
