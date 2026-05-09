"""
Comprehensive tests for all parsers.

Tests cover:
- JSON parser (with comments)
- YAML parser (simple cases)
- CSV parser (with header detection and type inference)
- TOML parser (simple cases)
- Round-trip tests (parse -> dump -> parse and compare)
- Format auto-detection
- Edge cases
"""

import os
import tempfile
import unittest

from datadiffforge.parsers.json_parser import JsonParser
from datadiffforge.parsers.yaml_parser import YamlParser
from datadiffforge.parsers.csv_parser import CsvParser
from datadiffforge.parsers.toml_parser import TomlParser
from datadiffforge.utils.file_utils import detect_format, get_parser, load_file, save_file


class TestJsonParser(unittest.TestCase):
    """Tests for the JSON parser."""

    def setUp(self):
        self.parser = JsonParser()

    def test_format_name(self):
        """Parser should report correct format name."""
        self.assertEqual(self.parser.format_name, "json")

    def test_file_extensions(self):
        """Parser should report correct file extensions."""
        self.assertIn(".json", self.parser.file_extensions)

    def test_load_simple_object(self):
        """Loading a simple JSON object should work."""
        data = self.parser.load('{"a": 1, "b": "hello"}')
        self.assertEqual(data, {"a": 1, "b": "hello"})

    def test_load_nested_object(self):
        """Loading nested JSON should work."""
        content = '{"a": {"b": {"c": 42}}}'
        data = self.parser.load(content)
        self.assertEqual(data, {"a": {"b": {"c": 42}}})

    def test_load_array(self):
        """Loading a JSON array should work."""
        data = self.parser.load('[1, 2, 3]')
        self.assertEqual(data, [1, 2, 3])

    def test_load_with_hash_comments(self):
        """Loading JSON with # comments should strip them."""
        content = '{"a": 1, # this is a comment\n"b": 2}'
        data = self.parser.load(content)
        self.assertEqual(data, {"a": 1, "b": 2})

    def test_load_with_double_slash_comments(self):
        """Loading JSON with // comments should strip them."""
        content = '{"a": 1, // this is a comment\n"b": 2}'
        data = self.parser.load(content)
        self.assertEqual(data, {"a": 1, "b": 2})

    def test_load_with_block_comments(self):
        """Loading JSON with block comments should strip them."""
        content = '{"a": 1, /* block comment */ "b": 2}'
        data = self.parser.load(content)
        self.assertEqual(data, {"a": 1, "b": 2})

    def test_dump_simple(self):
        """Dumping a simple object should produce valid JSON."""
        result = self.parser.dump({"a": 1, "b": "hello"})
        data = self.parser.load(result)
        self.assertEqual(data, {"a": 1, "b": "hello"})

    def test_round_trip(self):
        """Round-trip (load -> dump -> load) should preserve data."""
        original = {"a": 1, "b": [1, 2, 3], "c": {"d": "hello"}}
        dumped = self.parser.dump(original)
        loaded = self.parser.load(dumped)
        self.assertEqual(loaded, original)

    def test_load_file(self):
        """Loading from a file should work."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"a": 1, "b": "test"}')
            f.flush()
            data = self.parser.load_file(f.name)
            os.unlink(f.name)
        self.assertEqual(data, {"a": 1, "b": "test"})

    def test_dump_file(self):
        """Dumping to a file should work."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            fname = f.name
        self.parser.dump_file({"a": 1}, fname)
        data = self.parser.load_file(fname)
        os.unlink(fname)
        self.assertEqual(data, {"a": 1})

    def test_empty_object(self):
        """Loading empty object should return empty dict."""
        data = self.parser.load('{}')
        self.assertEqual(data, {})

    def test_empty_array(self):
        """Loading empty array should return empty list."""
        data = self.parser.load('[]')
        self.assertEqual(data, [])


class TestYamlParser(unittest.TestCase):
    """Tests for the YAML parser."""

    def setUp(self):
        self.parser = YamlParser()

    def test_format_name(self):
        self.assertEqual(self.parser.format_name, "yaml")

    def test_file_extensions(self):
        self.assertIn(".yaml", self.parser.file_extensions)
        self.assertIn(".yml", self.parser.file_extensions)

    def test_load_simple_mapping(self):
        """Loading a simple mapping should work."""
        content = "a: 1\nb: hello\n"
        data = self.parser.load(content)
        self.assertEqual(data, {"a": 1, "b": "hello"})

    def test_load_nested_mapping(self):
        """Loading nested mappings should work."""
        content = "a:\n  b: 1\n  c: 2\n"
        data = self.parser.load(content)
        self.assertEqual(data, {"a": {"b": 1, "c": 2}})

    def test_load_sequence(self):
        """Loading a sequence should work."""
        content = "- item1\n- item2\n- item3\n"
        data = self.parser.load(content)
        self.assertEqual(data, ["item1", "item2", "item3"])

    def test_load_numbers(self):
        """Loading numbers should infer correct types."""
        content = "int_val: 42\nfloat_val: 3.14\n"
        data = self.parser.load(content)
        self.assertEqual(data["int_val"], 42)
        self.assertIsInstance(data["int_val"], int)
        self.assertAlmostEqual(data["float_val"], 3.14)

    def test_load_booleans(self):
        """Loading booleans should infer correctly."""
        content = "true_val: true\nfalse_val: false\n"
        data = self.parser.load(content)
        self.assertIs(data["true_val"], True)
        self.assertIs(data["false_val"], False)

    def test_load_null(self):
        """Loading null values should work."""
        content = "empty: null\n"
        data = self.parser.load(content)
        self.assertIsNone(data["empty"])

    def test_load_quoted_strings(self):
        """Loading quoted strings should strip quotes."""
        content = 'a: "hello"\nb: \'world\'\n'
        data = self.parser.load(content)
        self.assertEqual(data["a"], "hello")
        self.assertEqual(data["b"], "world")

    def test_load_sequence_of_mappings(self):
        """Loading a sequence of mappings should work."""
        content = "- name: Alice\n  age: 30\n- name: Bob\n  age: 25\n"
        data = self.parser.load(content)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Alice")
        self.assertEqual(data[1]["name"], "Bob")

    def test_dump_simple(self):
        """Dumping a simple mapping should produce valid YAML."""
        data = {"a": 1, "b": "hello"}
        result = self.parser.dump(data)
        self.assertIn("a: 1", result)
        self.assertIn("b: hello", result)

    def test_round_trip_simple(self):
        """Round-trip should preserve simple data."""
        original = {"a": 1, "b": "hello", "c": True, "d": None}
        dumped = self.parser.dump(original)
        loaded = self.parser.load(dumped)
        self.assertEqual(loaded, original)

    def test_round_trip_nested(self):
        """Round-trip should preserve nested data."""
        original = {"a": {"b": 1, "c": [1, 2, 3]}}
        dumped = self.parser.dump(original)
        loaded = self.parser.load(dumped)
        self.assertEqual(loaded, original)

    def test_empty_content(self):
        """Empty content should return empty dict."""
        data = self.parser.load("")
        self.assertEqual(data, {})

    def test_comments_ignored(self):
        """Comments should be ignored during loading."""
        content = "# This is a comment\na: 1\n# Another comment\nb: 2\n"
        data = self.parser.load(content)
        self.assertEqual(data, {"a": 1, "b": 2})


class TestCsvParser(unittest.TestCase):
    """Tests for the CSV parser."""

    def setUp(self):
        self.parser = CsvParser()

    def test_format_name(self):
        self.assertEqual(self.parser.format_name, "csv")

    def test_file_extensions(self):
        self.assertIn(".csv", self.parser.file_extensions)

    def test_load_simple(self):
        """Loading simple CSV should work."""
        content = "name,age\nAlice,30\nBob,25\n"
        data = self.parser.load(content)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Alice")
        self.assertEqual(data[0]["age"], 30)

    def test_load_with_type_inference(self):
        """Type inference should work for numeric values."""
        content = "name,score,active\nAlice,95,true\nBob,87,false\n"
        data = self.parser.load(content)
        self.assertEqual(data[0]["score"], 95)
        self.assertIsInstance(data[0]["score"], int)
        self.assertIs(data[0]["active"], True)
        self.assertIs(data[1]["active"], False)

    def test_load_no_header(self):
        """CSV without detectable header should use generated column names."""
        content = "1,2,3\n4,5,6\n"
        data = self.parser.load(content)
        self.assertIn("column_0", data[0])
        self.assertEqual(data[0]["column_0"], 1)

    def test_dump_simple(self):
        """Dumping should produce valid CSV."""
        data = [{"name": "Alice", "age": 30}]
        result = self.parser.dump(data)
        self.assertIn("Alice", result)
        self.assertIn("30", result)

    def test_round_trip(self):
        """Round-trip should preserve data."""
        original = [
            {"name": "Alice", "age": 30, "active": True},
            {"name": "Bob", "age": 25, "active": False},
        ]
        dumped = self.parser.dump(original)
        loaded = self.parser.load(dumped)
        # Compare field by field since types may differ after round-trip
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["name"], "Alice")
        self.assertEqual(loaded[0]["age"], 30)

    def test_empty_content(self):
        """Empty content should return empty list."""
        data = self.parser.load("")
        self.assertEqual(data, [])

    def test_delimiter_detection_semicolon(self):
        """Semicolon delimiter should be detected."""
        content = "name;age\nAlice;30\n"
        data = self.parser.load(content)
        self.assertEqual(data[0]["name"], "Alice")
        self.assertEqual(data[0]["age"], 30)

    def test_dump_empty(self):
        """Dumping empty list should return empty string."""
        result = self.parser.dump([])
        self.assertEqual(result, "")


class TestTomlParser(unittest.TestCase):
    """Tests for the TOML parser."""

    def setUp(self):
        self.parser = TomlParser()

    def test_format_name(self):
        self.assertEqual(self.parser.format_name, "toml")

    def test_file_extensions(self):
        self.assertIn(".toml", self.parser.file_extensions)

    def test_load_simple(self):
        """Loading simple key-value pairs should work."""
        content = 'title = "Hello"\nversion = 42\n'
        data = self.parser.load(content)
        self.assertEqual(data["title"], "Hello")
        self.assertEqual(data["version"], 42)

    def test_load_sections(self):
        """Loading sections should work."""
        content = '[database]\nhost = "localhost"\nport = 5432\n'
        data = self.parser.load(content)
        self.assertEqual(data["database"]["host"], "localhost")
        self.assertEqual(data["database"]["port"], 5432)

    def test_load_nested_sections(self):
        """Loading nested sections should work."""
        content = '[server]\n[server.ssl]\nenabled = true\n'
        data = self.parser.load(content)
        self.assertEqual(data["server"]["ssl"]["enabled"], True)

    def test_load_arrays(self):
        """Loading arrays should work."""
        content = 'ports = [8080, 8081, 8082]\n'
        data = self.parser.load(content)
        self.assertEqual(data["ports"], [8080, 8081, 8082])

    def test_load_booleans(self):
        """Loading booleans should work."""
        content = 'debug = true\nverbose = false\n'
        data = self.parser.load(content)
        self.assertIs(data["debug"], True)
        self.assertIs(data["verbose"], False)

    def test_load_floats(self):
        """Loading floats should work."""
        content = 'pi = 3.14\n'
        data = self.parser.load(content)
        self.assertAlmostEqual(data["pi"], 3.14)

    def test_load_inline_table(self):
        """Loading inline tables should work."""
        content = '[server]\nenv = {name = "prod", region = "us-east"}\n'
        data = self.parser.load(content)
        self.assertEqual(data["server"]["env"]["name"], "prod")
        self.assertEqual(data["server"]["env"]["region"], "us-east")

    def test_load_comments(self):
        """Comments should be ignored."""
        content = '# Configuration file\ntitle = "Test" # app title\n'
        data = self.parser.load(content)
        self.assertEqual(data["title"], "Test")

    def test_dump_simple(self):
        """Dumping simple data should produce valid TOML."""
        data = {"title": "Hello", "version": 42}
        result = self.parser.dump(data)
        self.assertIn('title = "Hello"', result)
        self.assertIn("version = 42", result)

    def test_dump_sections(self):
        """Dumping sections should produce valid TOML."""
        data = {"database": {"host": "localhost", "port": 5432}}
        result = self.parser.dump(data)
        self.assertIn("[database]", result)
        self.assertIn('host = "localhost"', result)

    def test_round_trip_simple(self):
        """Round-trip should preserve simple data."""
        original = {"title": "Test", "version": 1, "debug": True}
        dumped = self.parser.dump(original)
        loaded = self.parser.load(dumped)
        self.assertEqual(loaded, original)

    def test_round_trip_nested(self):
        """Round-trip should preserve nested data."""
        original = {"server": {"host": "localhost", "port": 8080}}
        dumped = self.parser.dump(original)
        loaded = self.parser.load(dumped)
        self.assertEqual(loaded, original)

    def test_empty_content(self):
        """Empty content should return empty dict."""
        data = self.parser.load("")
        self.assertEqual(data, {})

    def test_string_escapes(self):
        """String escape sequences should be handled."""
        content = 'msg = "hello\\nworld"\n'
        data = self.parser.load(content)
        self.assertEqual(data["msg"], "hello\nworld")


class TestFormatDetection(unittest.TestCase):
    """Tests for format auto-detection."""

    def test_detect_json(self):
        self.assertEqual(detect_format("config.json"), "json")

    def test_detect_yaml(self):
        self.assertEqual(detect_format("config.yaml"), "yaml")
        self.assertEqual(detect_format("config.yml"), "yaml")

    def test_detect_csv(self):
        self.assertEqual(detect_format("data.csv"), "csv")

    def test_detect_toml(self):
        self.assertEqual(detect_format("config.toml"), "toml")

    def test_detect_unknown(self):
        with self.assertRaises(ValueError):
            detect_format("config.xyz")

    def test_get_parser_by_name(self):
        parser = get_parser(format_name="json")
        self.assertIsInstance(parser, JsonParser)

    def test_get_parser_by_filepath(self):
        parser = get_parser(filepath="config.yaml")
        self.assertIsInstance(parser, YamlParser)


class TestFileUtils(unittest.TestCase):
    """Tests for file utility functions."""

    def test_save_and_load(self):
        """Save and load should be symmetric."""
        data = {"a": 1, "b": [1, 2, 3]}
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            fname = f.name
        try:
            save_file(data, fname)
            loaded = load_file(fname)
            self.assertEqual(loaded, data)
        finally:
            os.unlink(fname)

    def test_save_and_load_yaml(self):
        """Save and load YAML should be symmetric for simple data."""
        data = {"a": 1, "b": "hello", "c": True}
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            fname = f.name
        try:
            save_file(data, fname)
            loaded = load_file(fname)
            self.assertEqual(loaded, data)
        finally:
            os.unlink(fname)


if __name__ == "__main__":
    unittest.main()
