"""
Comprehensive tests for the core diff engine.

Tests cover:
- Nested dict diff
- List diff (order-sensitive)
- Type change detection
- Primitive diff
- None value handling
- Path tracking
- Ignore paths
- Depth limiting
- Key normalization
- Statistics
- Edge cases
"""

import unittest

from datadiffforge.core.types import DiffOp, DiffResult, Change
from datadiffforge.core.differ import diff, deep_diff
from datadiffforge.core.path import Path


class TestDiffPrimitives(unittest.TestCase):
    """Tests for primitive value comparisons."""

    def test_identical_strings(self):
        """Identical strings should produce no changes."""
        result = diff("hello", "hello")
        self.assertFalse(result.has_changes)
        self.assertEqual(result.total_changes, 0)

    def test_different_strings(self):
        """Different strings should produce one MODIFIED change."""
        result = diff("hello", "world")
        self.assertTrue(result.has_changes)
        self.assertEqual(result.total_changes, 1)
        self.assertEqual(result.changes[0].op, DiffOp.MODIFIED)
        self.assertEqual(result.changes[0].path, "$")

    def test_identical_numbers(self):
        """Identical numbers should produce no changes."""
        result = diff(42, 42)
        self.assertFalse(result.has_changes)

    def test_different_numbers(self):
        """Different numbers should produce one MODIFIED change."""
        result = diff(42, 99)
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].op, DiffOp.MODIFIED)

    def test_identical_booleans(self):
        """Identical booleans should produce no changes."""
        result = diff(True, True)
        self.assertFalse(result.has_changes)

    def test_different_booleans(self):
        """Different booleans should produce one MODIFIED change."""
        result = diff(True, False)
        self.assertTrue(result.has_changes)

    def test_none_vs_none(self):
        """Two None values should produce no changes."""
        result = diff(None, None)
        self.assertFalse(result.has_changes)

    def test_none_vs_value(self):
        """None vs a value should produce an ADDED change."""
        result = diff(None, "hello")
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].op, DiffOp.ADDED)

    def test_value_vs_none(self):
        """A value vs None should produce a REMOVED change."""
        result = diff("hello", None)
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].op, DiffOp.REMOVED)


class TestDiffDicts(unittest.TestCase):
    """Tests for dictionary comparisons."""

    def test_identical_dicts(self):
        """Identical dicts should produce no changes."""
        data = {"a": 1, "b": 2}
        result = diff(data, data)
        self.assertFalse(result.has_changes)

    def test_added_key(self):
        """A key present only in right should be ADDED."""
        result = diff({"a": 1}, {"a": 1, "b": 2})
        self.assertTrue(result.has_changes)
        self.assertEqual(result.total_changes, 1)
        self.assertEqual(result.changes[0].op, DiffOp.ADDED)
        self.assertEqual(result.changes[0].path, "$.b")

    def test_removed_key(self):
        """A key present only in left should be REMOVED."""
        result = diff({"a": 1, "b": 2}, {"a": 1})
        self.assertTrue(result.has_changes)
        self.assertEqual(result.total_changes, 1)
        self.assertEqual(result.changes[0].op, DiffOp.REMOVED)
        self.assertEqual(result.changes[0].path, "$.b")

    def test_modified_value(self):
        """A changed value should be MODIFIED."""
        result = diff({"a": 1}, {"a": 2})
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].op, DiffOp.MODIFIED)
        self.assertEqual(result.changes[0].path, "$.a")

    def test_nested_dict_diff(self):
        """Nested dicts should track full path."""
        left = {"a": {"b": {"c": 1}}}
        right = {"a": {"b": {"c": 2}}}
        result = diff(left, right)
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].path, "$.a.b.c")
        self.assertEqual(result.changes[0].op, DiffOp.MODIFIED)

    def test_deeply_nested_dict(self):
        """Deeply nested dicts should track full path and depth."""
        left = {"l1": {"l2": {"l3": {"l4": {"l5": "old"}}}}}
        right = {"l1": {"l2": {"l3": {"l4": {"l5": "new"}}}}}
        result = diff(left, right)
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].path, "$.l1.l2.l3.l4.l5")
        self.assertEqual(result.changes[0].depth, 5)
        self.assertEqual(result.max_depth, 5)

    def test_multiple_changes(self):
        """Multiple changes should all be detected."""
        left = {"a": 1, "b": 2, "c": 3}
        right = {"a": 1, "b": 99, "d": 4}
        result = diff(left, right)
        self.assertTrue(result.has_changes)
        self.assertEqual(result.total_changes, 3)
        ops = {c.op for c in result.changes}
        self.assertIn(DiffOp.MODIFIED, ops)
        self.assertIn(DiffOp.REMOVED, ops)
        self.assertIn(DiffOp.ADDED, ops)

    def test_empty_dicts(self):
        """Two empty dicts should produce no changes."""
        result = diff({}, {})
        self.assertFalse(result.has_changes)

    def test_empty_vs_nonempty(self):
        """Empty dict vs non-empty should detect all keys as added."""
        result = diff({}, {"a": 1, "b": 2})
        self.assertTrue(result.has_changes)
        self.assertEqual(result.total_changes, 2)
        self.assertEqual(result.added_count, 2)


class TestDiffLists(unittest.TestCase):
    """Tests for list comparisons."""

    def test_identical_lists(self):
        """Identical lists should produce no changes."""
        data = [1, 2, 3]
        result = diff(data, data)
        self.assertFalse(result.has_changes)

    def test_added_item(self):
        """Extra item at end of right list should be ADDED."""
        result = diff([1, 2], [1, 2, 3])
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].op, DiffOp.ADDED)
        self.assertEqual(result.changes[0].path, "$[2]")

    def test_removed_item(self):
        """Missing item at end should be REMOVED."""
        result = diff([1, 2, 3], [1, 2])
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].op, DiffOp.REMOVED)
        self.assertEqual(result.changes[0].path, "$[2]")

    def test_modified_item(self):
        """Changed item at same index should be MODIFIED."""
        result = diff([1, 2, 3], [1, 99, 3])
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].op, DiffOp.MODIFIED)
        self.assertEqual(result.changes[0].path, "$[1]")

    def test_nested_list_diff(self):
        """Nested lists should track full path."""
        left = [[1, 2], [3, 4]]
        right = [[1, 2], [3, 99]]
        result = diff(left, right)
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].path, "$[1][1]")

    def test_list_of_dicts(self):
        """List containing dicts should recurse into dict comparison."""
        left = [{"name": "Alice", "age": 30}]
        right = [{"name": "Alice", "age": 31}]
        result = diff(left, right)
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].path, "$[0].age")

    def test_empty_lists(self):
        """Two empty lists should produce no changes."""
        result = diff([], [])
        self.assertFalse(result.has_changes)


class TestTypeChanges(unittest.TestCase):
    """Tests for type change detection."""

    def test_string_to_number(self):
        """String changed to number should be TYPE_CHANGED."""
        result = diff("hello", 42)
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].op, DiffOp.TYPE_CHANGED)
        self.assertEqual(result.changes[0].old_type, "str")
        self.assertEqual(result.changes[0].new_type, "int")

    def test_dict_to_list(self):
        """Dict changed to list should be TYPE_CHANGED."""
        result = diff({"a": 1}, [1, 2])
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].op, DiffOp.TYPE_CHANGED)

    def test_number_to_bool(self):
        """Number changed to bool should be TYPE_CHANGED."""
        result = diff(42, True)
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].op, DiffOp.TYPE_CHANGED)

    def test_nested_type_change(self):
        """Type change in nested structure should track path."""
        left = {"a": {"b": [1, 2]}}
        right = {"a": {"b": "string"}}
        result = diff(left, right)
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].op, DiffOp.TYPE_CHANGED)
        self.assertEqual(result.changes[0].path, "$.a.b")


class TestIgnorePaths(unittest.TestCase):
    """Tests for path ignoring functionality."""

    def test_ignore_single_path(self):
        """Ignoring a specific path should exclude changes at that path."""
        left = {"a": 1, "b": 2}
        right = {"a": 99, "b": 2}
        result = diff(left, right, ignore_paths=["$.a"])
        self.assertFalse(result.has_changes)

    def test_ignore_wildcard(self):
        """Ignoring with wildcard should match multiple paths."""
        left = {"a": {"x": 1}, "b": {"x": 2}}
        right = {"a": {"x": 99}, "b": {"x": 99}}
        result = diff(left, right, ignore_paths=["$.a.*"])
        self.assertTrue(result.has_changes)
        self.assertEqual(result.total_changes, 1)
        self.assertEqual(result.changes[0].path, "$.b.x")

    def test_ignore_double_star(self):
        """Double-star wildcard should match any depth."""
        left = {"a": {"b": {"c": 1, "d": 2}}}
        right = {"a": {"b": {"c": 99, "d": 99}}}
        result = diff(left, right, ignore_paths=["$.a.**"])
        self.assertFalse(result.has_changes)

    def test_ignore_non_matching(self):
        """Non-matching ignore patterns should not affect results."""
        left = {"a": 1}
        right = {"a": 99}
        result = diff(left, right, ignore_paths=["$.b"])
        self.assertTrue(result.has_changes)


class TestDepthLimit(unittest.TestCase):
    """Tests for depth limiting functionality."""

    def test_unlimited_depth(self):
        """Without depth limit, all levels should be compared."""
        left = {"a": {"b": {"c": 1}}}
        right = {"a": {"b": {"c": 99}}}
        result = diff(left, right)
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].path, "$.a.b.c")

    def test_limited_depth(self):
        """With depth limit, deeper changes should not be detected."""
        left = {"a": {"b": {"c": 1}}}
        right = {"a": {"b": {"c": 99}}}
        result = diff(left, right, max_depth=2)
        self.assertFalse(result.has_changes)

    def test_depth_limit_boundary(self):
        """Depth limit should include the specified depth level."""
        left = {"a": {"b": 1}}
        right = {"a": {"b": 99}}
        result = diff(left, right, max_depth=2)
        self.assertTrue(result.has_changes)


class TestStatistics(unittest.TestCase):
    """Tests for diff statistics."""

    def test_counts(self):
        """Statistics should correctly count each operation type."""
        left = {"a": 1, "b": "hello", "c": [1, 2], "d": True}
        right = {"a": 2, "e": "new", "c": "changed", "d": 42}
        result = diff(left, right)
        self.assertEqual(result.modified_count, 1)  # a
        self.assertEqual(result.added_count, 1)     # e
        self.assertEqual(result.removed_count, 1)   # b
        self.assertEqual(result.type_changed_count, 2)  # c, d
        self.assertEqual(result.total_changes, 5)

    def test_stats_by_depth(self):
        """Statistics by depth should be tracked correctly."""
        left = {"a": {"b": 1}}
        right = {"a": {"b": 2}, "c": 3}
        result = diff(left, right)
        self.assertIn(2, result.stats_by_depth)  # $.a.b at depth 2
        self.assertIn(0, result.stats_by_depth)  # $.c at depth 0


class TestPath(unittest.TestCase):
    """Tests for the Path class."""

    def test_root_path(self):
        """Root path should be '$'."""
        p = Path.root()
        self.assertEqual(str(p), "$")

    def test_key_navigation(self):
        """Key navigation should produce correct path."""
        p = Path.root().key("users").key("name")
        self.assertEqual(str(p), "$.users.name")

    def test_index_navigation(self):
        """Index navigation should produce correct path."""
        p = Path.root().key("items").index(0)
        self.assertEqual(str(p), "$.items[0]")

    def test_mixed_navigation(self):
        """Mixed key/index navigation should produce correct path."""
        p = Path.root().key("users").index(0).key("name")
        self.assertEqual(str(p), "$.users[0].name")

    def test_parent(self):
        """Parent should return the path without the last segment."""
        p = Path.root().key("a").key("b")
        self.assertEqual(str(p.parent()), "$.a")

    def test_depth(self):
        """Depth should return the number of segments."""
        p = Path.root().key("a").key("b").index(0)
        self.assertEqual(p.depth, 3)

    def test_from_string(self):
        """Parsing from string should produce equivalent path."""
        p1 = Path.from_string("$.users[0].name")
        p2 = Path.root().key("users").index(0).key("name")
        self.assertEqual(str(p1), str(p2))

    def test_equality(self):
        """Paths with same segments should be equal."""
        p1 = Path.root().key("a").key("b")
        p2 = Path.root().key("a").key("b")
        self.assertEqual(p1, p2)

    def test_glob_match(self):
        """Glob matching should work correctly."""
        p = Path.from_string("$.users[0].name")
        self.assertTrue(p.matches_glob("$.users.*.name"))
        self.assertTrue(p.matches_glob("$.users.**"))
        self.assertFalse(p.matches_glob("$.users.*.age"))


class TestDiffLabels(unittest.TestCase):
    """Tests for diff result labels."""

    def test_custom_labels(self):
        """Custom labels should be stored in the result."""
        result = diff({"a": 1}, {"a": 2}, left_label="file1.json", right_label="file2.json")
        self.assertEqual(result.left_label, "file1.json")
        self.assertEqual(result.right_label, "file2.json")


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases."""

    def test_large_dict(self):
        """Large dicts should be handled correctly."""
        left = {f"key_{i}": i for i in range(100)}
        right = {f"key_{i}": i for i in range(100)}
        right["key_50"] = -1
        right["key_new"] = 999
        result = diff(left, right)
        self.assertTrue(result.has_changes)
        self.assertEqual(result.total_changes, 2)

    def test_empty_vs_none(self):
        """Empty dict vs None should be detected as a change (REMOVED since None handling takes priority)."""
        result = diff({}, None)
        self.assertTrue(result.has_changes)
        self.assertEqual(result.changes[0].op, DiffOp.REMOVED)

    def test_special_characters_in_keys(self):
        """Keys with special characters should be handled."""
        left = {"key with spaces": 1}
        right = {"key with spaces": 2}
        result = diff(left, right)
        self.assertTrue(result.has_changes)

    def test_unicode_values(self):
        """Unicode values should be compared correctly."""
        left = {"name": "Hello"}
        right = {"name": "Hello"}
        result = diff(left, right)
        self.assertFalse(result.has_changes)

    def test_summary(self):
        """Summary should return formatted string."""
        result = diff({"a": 1}, {"a": 2})
        summary = result.summary()
        self.assertIn("Total changes: 1", summary)
        self.assertIn("Modified: 1", summary)

    def test_to_dict(self):
        """to_dict should serialize correctly."""
        result = diff({"a": 1}, {"a": 2})
        d = result.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["total_changes"], 1)
        self.assertEqual(len(d["changes"]), 1)


if __name__ == "__main__":
    unittest.main()
