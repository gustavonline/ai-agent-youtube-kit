"""A small dependency-free JSON Schema subset plus domain validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .errors import ACSUserError


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def _type_matches(value: Any, schema_type: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(schema_type, True)


def validate_json(value: Any, schema: dict[str, Any], path: str = "$") -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    expected = schema.get("type")
    if expected and not _type_matches(value, expected):
        return [ValidationIssue(path, f"expected {expected}")]

    if "const" in schema and value != schema["const"]:
        issues.append(ValidationIssue(path, f"must equal {schema['const']!r}"))
    if "enum" in schema and value not in schema["enum"]:
        issues.append(ValidationIssue(path, f"must be one of {schema['enum']}"))
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            issues.append(ValidationIssue(path, f"must contain at least {schema['minLength']} characters"))
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            issues.append(ValidationIssue(path, "does not match the required pattern"))
    if isinstance(value, (int, float)) and "minimum" in schema and value < schema["minimum"]:
        issues.append(ValidationIssue(path, f"must be >= {schema['minimum']}"))
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            issues.append(ValidationIssue(path, f"must contain at least {schema['minItems']} items"))
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            issues.append(ValidationIssue(path, f"must contain at most {schema['maxItems']} items"))
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                issues.extend(validate_json(item, item_schema, f"{path}[{index}]"))
    if isinstance(value, dict):
        for required in schema.get("required", []):
            if required not in value:
                issues.append(ValidationIssue(path, f"missing required property {required!r}"))
        properties = schema.get("properties", {})
        for key, child in value.items():
            if key in properties:
                issues.extend(validate_json(child, properties[key], f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                issues.append(ValidationIssue(f"{path}.{key}", "additional property is not allowed"))
    for alternative in schema.get("oneOf", []):
        if not validate_json(value, alternative, path):
            break
    else:
        if schema.get("oneOf"):
            issues.append(ValidationIssue(path, "does not match any allowed shape"))
    return issues


def require_valid(value: Any, schema: dict[str, Any], label: str) -> None:
    issues = validate_json(value, schema)
    if issues:
        rendered = "\n".join(f"- {issue}" for issue in issues)
        raise ACSUserError(f"{label} failed validation:\n{rendered}")
