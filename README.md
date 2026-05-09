# DataDiffForge

A lightweight structured data diff and intelligent merge engine.

Pure Python 3.8+ with zero external dependencies.

## Features

- Deep diff for nested dicts, lists, and primitives
- JSONPath tracking for each change
- Multiple merge strategies (keep-both, left-wins, right-wins, smart)
- Support for JSON, YAML, CSV, and TOML formats
- Multiple output formats (terminal, JSON, HTML, Markdown)
- File watching mode
- Snapshot management

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Diff two files
datadiff diff file1.json file2.json

# Diff with HTML output
datadiff diff config.yaml config2.yaml -f html -o diff.html

# Merge two files
datadiff merge left.json right.json -s smart -o merged.json

# Create a snapshot
datadiff snapshot data.json -l backup

# Watch files for changes
datadiff watch config.yaml config-live.yaml -n 5
```
