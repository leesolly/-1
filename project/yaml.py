"""Minimal YAML loader supporting the subset used in configuration files."""

from __future__ import annotations

import ast
from typing import Any, Tuple


def _parse_value(value: str) -> Any:
    text = value.strip()
    if text.lower() in {"true", "false"}:
        return text.lower() == "true"
    if text == "":
        return {}
    try:
        return ast.literal_eval(text)
    except Exception:
        return text


def _parse_lines(lines: list[str], start: int, indent: int) -> Tuple[int, Any]:
    mapping: dict[str, Any] = {}
    index = start
    while index < len(lines):
        raw_line = lines[index]
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            index += 1
            continue
        current_indent = len(raw_line) - len(raw_line.lstrip(" "))
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ValueError("Invalid indentation in YAML subset parser")
        line = raw_line.strip()
        if line.startswith("-"):
            raise ValueError("List items not supported in top-level positions without keys")
        if ":" not in line:
            raise ValueError(f"Invalid line: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        if value.strip() == "":
            index, child = _parse_lines(lines, index + 1, indent + 2)
            mapping[key] = child
        else:
            mapping[key] = _parse_value(value)
            index += 1
    return index, mapping


def safe_load(stream: str) -> Any:
    if hasattr(stream, "read"):
        content = stream.read()
    else:
        content = stream
    lines = content.splitlines()
    _, data = _parse_lines(lines, 0, 0)
    return data
