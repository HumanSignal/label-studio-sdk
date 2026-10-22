import inspect
import random
import sys
from datetime import datetime

import jsonschema
import pytest
from . import configs as c
from .test_data_generation import _INVARIANT_LABEL_ARRAY_CONFIGS, LABEL_ARRAY_TAG_CONFIGS

from label_studio_sdk.label_interface import LabelInterface, control_tags
from label_studio_sdk.label_interface.schema_example import generate_example

SEEDS = range(20)

# Control tags no shared config exercises
_EXTRA_CONFIGS = {
    "MagicWandTag": """
    <View>
      <Image name="img" value="$image"/>
      <MagicWand name="label" toName="img"/>
    </View>
    """,
}


def _all_configs():
    configs = list(LABEL_ARRAY_TAG_CONFIGS.values()) + list(_INVARIANT_LABEL_ARRAY_CONFIGS.values())
    configs += [value for value in vars(c).values() if isinstance(value, str) and "<View" in value]
    configs += list(_EXTRA_CONFIGS.values())
    return configs


def _control_schemas():
    """(tag class name, schema) for every control tag that sample generation runs on."""
    schemas = {}
    for config in _all_configs():
        try:
            li = LabelInterface(config)
        except Exception:
            continue  # some shared configs are intentionally invalid
        for control in li.controls:
            schema = control.to_json_schema()
            if LabelInterface._can_generate_sample_region(control, schema):
                schemas.setdefault(f"{type(control).__name__}:{control.name}", schema)
    return schemas


CONTROL_SCHEMAS = _control_schemas()


def _validate(instance, schema):
    jsonschema.Draft202012Validator(schema).validate(instance)


@pytest.mark.parametrize("schema", [{"const": "rle"}, {"type": "string", "enum": ["rle"]}])
def test_const_and_single_enum(schema):
    assert generate_example(schema) == "rle"


def test_enum_picks_declared_value():
    schema = {"type": "string", "enum": ["Cat", "Dog", "Bird"]}
    values = {generate_example(schema, random.Random(seed)) for seed in SEEDS}
    assert values <= {"Cat", "Dog", "Bird"}
    assert len(values) > 1, "enum values should vary across seeds"


@pytest.mark.parametrize(
    "schema",
    [
        {"type": "number", "minimum": 0, "maximum": 100},
        {"type": "number", "minimum": 0, "maximum": 0.3},
        {"type": "number", "minimum": 5},
        {"type": "number", "maximum": -5},
        {"type": "number"},
        {"type": "integer", "minimum": 0, "maximum": 255},
        {"type": "integer", "minimum": 3, "maximum": 3},
        {"type": "integer"},
    ],
)
def test_numbers_respect_bounds(schema):
    for seed in SEEDS:
        value = generate_example(schema, random.Random(seed))
        _validate(value, schema)
        if schema["type"] == "integer":
            assert isinstance(value, int)
        else:
            assert not float(value).is_integer(), "plain numbers must not look like integers (see oneOf)"


@pytest.mark.parametrize(
    "branches",
    [
        [{"type": "integer"}, {"type": "number"}],
        [{"type": "integer", "minimum": 0}, {"type": "number", "minimum": 0}],
        [{"type": "string"}, {"type": "array", "items": {"type": "string"}}],
    ],
)
def test_one_of_matches_exactly_one_branch(branches):
    # An integer satisfies both {"type": "integer"} and {"type": "number"}, which oneOf rejects
    schema = {"oneOf": branches}
    for seed in SEEDS:
        _validate(generate_example(schema, random.Random(seed)), schema)


def test_array_item_count_and_unique_enum_items():
    schema = {"type": "array", "items": {"type": "string", "enum": ["A", "B", "C"]}, "minItems": 2, "maxItems": 3}
    for seed in SEEDS:
        value = generate_example(schema, random.Random(seed))
        _validate(value, schema)
        assert len(value) == len(set(value)) == 2


def test_array_defaults_to_one_item_and_honours_max_items():
    assert len(generate_example({"type": "array", "items": {"type": "integer"}})) == 1
    assert generate_example({"type": "array", "items": {"type": "integer"}, "maxItems": 0}) == []


def test_nested_object_with_required_properties():
    schema = {
        "type": "object",
        "properties": {
            "points": {
                "type": "array",
                "items": {"type": "array", "items": {"type": "number", "minimum": 0, "maximum": 100}},
                "minItems": 3,
            },
            "closed": {"type": "boolean"},
            "labels": {"type": "array", "items": {"type": "string", "enum": ["Car"]}, "minItems": 1},
        },
        "required": ["points", "labels"],
        "additionalProperties": False,
    }
    for seed in SEEDS:
        value = generate_example(schema, random.Random(seed))
        _validate(value, schema)
        assert set(value) == {"points", "closed", "labels"}


def test_date_time_format_is_iso_8601():
    value = generate_example({"type": "string", "format": "date-time"})
    assert datetime.fromisoformat(value).tzinfo is not None


def test_nullable_type_list_prefers_non_null():
    assert isinstance(generate_example({"type": ["null", "integer"]}), int)


def test_seeded_rng_is_reproducible():
    schema = CONTROL_SCHEMAS[next(iter(CONTROL_SCHEMAS))]
    assert generate_example(schema, random.Random(7)) == generate_example(schema, random.Random(7))


def test_every_generatable_control_tag_is_covered():
    """New control tags must get a config here (or in the shared configs) to be checked below."""
    generatable = {
        name
        for name, cls in vars(control_tags).items()
        if inspect.isclass(cls)
        and issubclass(cls, control_tags.ControlTag)
        and cls is not control_tags.ControlTag
        and hasattr(cls, "_value_class")
    }
    covered = {key.split(":")[0] for key in CONTROL_SCHEMAS}
    assert generatable - covered == set(), "add a config for these tags to _EXTRA_CONFIGS"


@pytest.mark.parametrize("name", sorted(CONTROL_SCHEMAS))
def test_example_is_valid_for_every_control_tag_schema(name):
    schema = CONTROL_SCHEMAS[name]
    for seed in SEEDS:
        _validate(generate_example(schema, random.Random(seed)), schema)


def _sample_prediction_params():
    params = []
    for config in _all_configs():
        marks = []
        if "<Pairwise" in config:
            # Pre-existing: never produced a valid sample prediction with jsf either
            marks.append(pytest.mark.xfail(strict=True, reason="Pairwise sample predictions fail validation"))
        params.append(pytest.param(config, marks=marks))
    return params


@pytest.mark.parametrize("config", _sample_prediction_params())
def test_sample_prediction_and_annotation_validate(config):
    try:
        li = LabelInterface(config)
    except Exception:
        pytest.skip("intentionally invalid shared config")
    if not any(LabelInterface._can_generate_sample_region(ctl, ctl.to_json_schema()) for ctl in li.controls):
        pytest.skip("no control tag generates sample regions")
    for _ in SEEDS:
        prediction = li.generate_sample_prediction()
        assert prediction is not None and li.validate_prediction(prediction)


def test_jsf_is_not_imported():
    import label_studio_sdk.label_interface.interface  # noqa: F401

    assert "jsf" not in sys.modules
