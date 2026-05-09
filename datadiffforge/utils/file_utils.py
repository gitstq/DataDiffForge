"""
File utility functions for DataDiffForge.

Provides file reading/writing, format auto-detection, and
snapshot management functionality.
"""

import json
import os
import shutil
from datetime import datetime
from typing import Any, Dict, Optional

from ..parsers.base import ParserInterface
from ..parsers.json_parser import JsonParser
from ..parsers.yaml_parser import YamlParser
from ..parsers.csv_parser import CsvParser
from ..parsers.toml_parser import TomlParser


# Registry mapping file extensions to parser instances
_PARSER_REGISTRY: Dict[str, ParserInterface] = {}


def _get_parser_registry() -> Dict[str, ParserInterface]:
    """
    Get or create the parser registry.

    Returns:
        Dictionary mapping file extensions to parser instances.
    """
    if not _PARSER_REGISTRY:
        parsers = [JsonParser(), YamlParser(), CsvParser(), TomlParser()]
        for parser in parsers:
            for ext in parser.file_extensions:
                _PARSER_REGISTRY[ext] = parser
    return _PARSER_REGISTRY


def detect_format(filepath: str) -> str:
    """
    Detect the file format from the file extension.

    Args:
        filepath: Path to the file.

    Returns:
        The format name (e.g., 'json', 'yaml', 'csv', 'toml').

    Raises:
        ValueError: If the file extension is not recognized.
    """
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()

    registry = _get_parser_registry()
    if ext in registry:
        return registry[ext].format_name

    raise ValueError(
        f"Unsupported file format: '{ext}'. "
        f"Supported formats: {', '.join(sorted(set(p.format_name for p in registry.values())))}"
    )


def get_parser(format_name: Optional[str] = None, filepath: Optional[str] = None) -> ParserInterface:
    """
    Get the appropriate parser for a format or file.

    Args:
        format_name: Explicit format name (e.g., 'json').
        filepath: File path to auto-detect format from extension.

    Returns:
        The parser instance.

    Raises:
        ValueError: If no parser can be determined.
    """
    if format_name:
        registry = _get_parser_registry()
        for parser in registry.values():
            if parser.format_name == format_name:
                return parser
        raise ValueError(f"No parser found for format: '{format_name}'")

    if filepath:
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()
        registry = _get_parser_registry()
        if ext in registry:
            return registry[ext]
        raise ValueError(f"No parser found for file extension: '{ext}'")

    raise ValueError("Either format_name or filepath must be provided")


def load_file(filepath: str, format_name: Optional[str] = None) -> Any:
    """
    Load and parse a data file.

    Auto-detects the format from the file extension unless explicitly specified.

    Args:
        filepath: Path to the file to load.
        format_name: Optional explicit format name.

    Returns:
        The parsed Python data structure.
    """
    parser = get_parser(format_name=format_name, filepath=filepath)
    return parser.load_file(filepath)


def save_file(
    data: Any,
    filepath: str,
    format_name: Optional[str] = None,
) -> None:
    """
    Serialize data and save to a file.

    Auto-detects the format from the file extension unless explicitly specified.

    Args:
        data: The Python data structure to save.
        filepath: Path to the output file.
        format_name: Optional explicit format name.
    """
    parser = get_parser(format_name=format_name, filepath=filepath)
    parser.dump_file(data, filepath)


def save_snapshot(
    data: Any,
    output_dir: str,
    label: Optional[str] = None,
    format_name: str = "json",
) -> str:
    """
    Save a snapshot of data with a timestamp.

    Args:
        data: The data to snapshot.
        output_dir: Directory to save the snapshot in.
        label: Optional label for the snapshot.
        format_name: Format to save in (default: 'json').

    Returns:
        Path to the saved snapshot file.
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if label:
        filename = f"snapshot_{label}_{timestamp}.{format_name}"
    else:
        filename = f"snapshot_{timestamp}.{format_name}"

    filepath = os.path.join(output_dir, filename)
    save_file(data, filepath, format_name=format_name)

    return filepath


def write_output(content: str, output_path: Optional[str] = None) -> None:
    """
    Write content to a file or stdout.

    Args:
        content: The content to write.
        output_path: Optional file path. If None, prints to stdout.
    """
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print(content)
