"""Minimal JSON Schema example generator for sample predictions and annotations.

Replaces the ``jsf`` dependency, whose PyPI release fails on Python 3.14. It only supports
the JSON Schema subset produced by ``ControlTag.to_json_schema()``: ``type``, ``enum``,
``const``, ``oneOf``/``anyOf``, ``properties``/``required``, ``items``/``minItems``/
``maxItems``, ``minimum``/``maximum`` and ``format: date-time``. Values are random within
the schema's bounds; pass a seeded ``random.Random`` for reproducible output.
"""

import random
from datetime import datetime, timezone
from typing import Any, Optional

import jsonschema

# Range used when a numeric schema has no minimum and/or maximum
_DEFAULT_SPAN = 100
_ONE_OF_ATTEMPTS = 10


def generate_example(schema: dict, rng: Optional[random.Random] = None) -> Any:
    """Generate a value that is valid against ``schema``."""
    return _generate(schema, rng or random.Random())


def _generate(schema: dict, rng: random.Random) -> Any:
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        return rng.choice(schema["enum"])
    if "oneOf" in schema:
        return _generate_one_of(schema["oneOf"], rng)
    if "anyOf" in schema:
        return _generate(schema["anyOf"][0], rng)

    schema_type = schema.get("type")
    if isinstance(schema_type, list):
        schema_type = next((t for t in schema_type if t != "null"), "null")
    if schema_type is None and "properties" in schema:
        schema_type = "object"

    if schema_type == "object":
        return {name: _generate(prop, rng) for name, prop in schema.get("properties", {}).items()}
    if schema_type == "array":
        return _generate_array(schema, rng)
    if schema_type == "integer":
        low, high = _bounds(schema)
        return rng.randint(int(low), int(high))
    if schema_type == "number":
        return _generate_number(schema, rng)
    if schema_type == "boolean":
        return rng.choice([True, False])
    if schema_type == "string":
        if schema.get("format") == "date-time":
            return datetime.now(timezone.utc).isoformat()
        return "sample text"
    return None


def _generate_one_of(branches: list, rng: random.Random) -> Any:
    # A value must match exactly one branch: an integer satisfies both {"type": "integer"} and
    # {"type": "number"}, so keep generating until a candidate is unambiguous.
    validators = [jsonschema.Draft202012Validator(branch) for branch in branches]
    candidate = None
    for _ in range(_ONE_OF_ATTEMPTS):
        for branch in branches:
            candidate = _generate(branch, rng)
            if sum(validator.is_valid(candidate) for validator in validators) == 1:
                return candidate
    return candidate


def _generate_array(schema: dict, rng: random.Random) -> list:
    min_items = schema.get("minItems", 1)
    max_items = schema.get("maxItems")
    count = min_items if max_items is None else min(min_items, max_items)
    items = schema.get("items", {})
    if "enum" in items and len(items["enum"]) >= count:
        # avoid duplicate labels such as ["Cat", "Cat"]
        return rng.sample(items["enum"], count)
    return [_generate(items, rng) for _ in range(count)]


def _generate_number(schema: dict, rng: random.Random) -> float:
    low, high = _bounds(schema)
    value = round(rng.uniform(low, high), 2)
    if value.is_integer() and high > low:
        # keep it a non-integer so {"type": "number"} is distinguishable from integers in oneOf;
        # the step is at most a quarter of the range, so one direction always stays in bounds
        step = min(0.5, (high - low) / 4)
        value = value + step if value + step <= high else value - step
    return value


def _bounds(schema: dict) -> tuple:
    low = schema.get("minimum")
    high = schema.get("maximum")
    if low is None and high is None:
        return 0, _DEFAULT_SPAN
    if low is None:
        return high - _DEFAULT_SPAN, high
    if high is None:
        return low, low + _DEFAULT_SPAN
    return low, high
