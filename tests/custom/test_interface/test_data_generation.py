import pytest
from . import configs as c
from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.label_interface.control_tags import ControlTag
from label_studio_sdk.label_interface.object_tags import ObjectTag
from lxml.etree import Element

LABEL_ARRAY_TAG_CONFIGS = {
    "EllipseLabelsTag": """
    <View>
      <Image name="image" value="$image"/>
      <EllipseLabels name="label" toName="image">
        <Label value="Ellipse1"/>
        <Label value="Ellipse2"/>
      </EllipseLabels>
    </View>
    """,
    "KeyPointLabelsTag": """
    <View>
      <Image name="image" value="$image"/>
      <KeyPointLabels name="label" toName="image">
        <Label value="KeyPoint1"/>
        <Label value="KeyPoint2"/>
      </KeyPointLabels>
    </View>
    """,
    "VectorLabelsTag": """
    <View>
      <Image name="image" value="$image"/>
      <VectorLabels name="label" toName="image">
        <Label value="Vector1"/>
        <Label value="Vector2"/>
      </VectorLabels>
    </View>
    """,
    "OcrLabelsTag": """
    <View>
      <Image name="image" value="$image"/>
      <OcrLabels name="label" toName="image">
        <Label value="Ocr1"/>
        <Label value="Ocr2"/>
      </OcrLabels>
    </View>
    """,
    "PolygonLabelsTag": """
    <View>
      <Image name="image" value="$image"/>
      <PolygonLabels name="label" toName="image">
        <Label value="Polygon1"/>
        <Label value="Polygon2"/>
      </PolygonLabels>
    </View>
    """,
    "HyperTextLabelsTag": """
    <View>
      <HyperText name="hypertext" value="$hypertext"/>
      <HyperTextLabels name="label" toName="hypertext">
        <Label value="Html1"/>
        <Label value="Html2"/>
      </HyperTextLabels>
    </View>
    """,
    "ParagraphLabelsTag": """
    <View>
      <Paragraphs name="paragraphs" value="$paragraphs"/>
      <ParagraphLabels name="label" toName="paragraphs">
        <Label value="Para1"/>
        <Label value="Para2"/>
      </ParagraphLabels>
    </View>
    """,
    "VideoRectangleTag": """
    <View>
      <Video name="video" value="$video"/>
      <VideoRectangle name="label" toName="video">
        <Label value="VidRect1"/>
        <Label value="VidRect2"/>
      </VideoRectangle>
    </View>
    """,
    "VideoVectorLabelsTag": """
    <View>
      <Video name="video" value="$video"/>
      <VideoVectorLabels name="label" toName="video">
        <Label value="VidVec1"/>
        <Label value="VidVec2"/>
      </VideoVectorLabels>
    </View>
    """,
    "BrushLabelsTag": """
    <View>
      <Image name="image" value="$image"/>
      <BrushLabels name="label" toName="image">
        <Label value="Brush1"/>
        <Label value="Brush2"/>
      </BrushLabels>
    </View>
    """,
    "TimeSeriesLabelsTag": """
    <View>
      <TimeSeries name="ts" value="$ts" valueType="json">
        <Channel column="series"/>
      </TimeSeries>
      <TimeSeriesLabels name="label" toName="ts">
        <Label value="TS1"/>
        <Label value="TS2"/>
      </TimeSeriesLabels>
    </View>
    """,
}


def _all_subclasses(cls):
    for sub in cls.__subclasses__():
        yield sub
        yield from _all_subclasses(sub)


def test_generate_sample_task():
    conf = LabelInterface(c.SIMPLE_CONF)
    task = conf.generate_sample_task()
    value = c.VALUE[1:]

    print(task)

    assert value in task
    assert len(task[value])


@pytest.mark.parametrize("tag_name,config", list(LABEL_ARRAY_TAG_CONFIGS.items()))
def test_generate_sample_prediction_and_annotation(tag_name, config):
    """Parametrized regression test for hp-wgxy.

    Ensures generate_sample_prediction() and generate_sample_annotation()
    return non-None results and only use labels defined in the config.
    """
    li = LabelInterface(config)
    prediction = li.generate_sample_prediction()
    annotation = li.generate_sample_annotation()

    assert prediction is not None, f"{tag_name}: sample prediction is None"
    assert annotation is not None, f"{tag_name}: sample annotation is None"

    # Extract declared labels from the config
    control = li.get_control('label')
    declared_labels = set(control.labels)
    label_attr = control._label_attr_name

    for result in prediction["result"]:
        labels = result.get("value", {}).get(label_attr, [])
        assert all(label in declared_labels for label in labels), (
            f"{tag_name}: prediction uses undefined labels: {labels}"
        )
        assert len(labels) == 1, (
            f"{tag_name}: single-choice prediction should have exactly 1 label, got {labels}"
        )

    for result in annotation["result"]:
        labels = result.get("value", {}).get(label_attr, [])
        assert all(label in declared_labels for label in labels), (
            f"{tag_name}: annotation uses undefined labels: {labels}"
        )
        assert len(labels) == 1, (
            f"{tag_name}: single-choice annotation should have exactly 1 label, got {labels}"
        )


@pytest.mark.parametrize("tag_name,config", list(LABEL_ARRAY_TAG_CONFIGS.items()))
def test_generate_sample_prediction_and_annotation_multiple_choice(tag_name, config):
    """Multiple-choice variant: omit maxItems so JSF can produce >1 label."""
    # Inject choice="multiple" into the control tag line
    modified_config = config.replace(">", ' choice="multiple">', 1)
    li = LabelInterface(modified_config)
    prediction = li.generate_sample_prediction()
    annotation = li.generate_sample_annotation()

    assert prediction is not None, f"{tag_name} (multiple): sample prediction is None"
    assert annotation is not None, f"{tag_name} (multiple): sample annotation is None"

    control = li.get_control('label')
    declared_labels = set(control.labels)
    label_attr = control._label_attr_name

    for result in prediction["result"]:
        labels = result.get("value", {}).get(label_attr, [])
        assert all(label in declared_labels for label in labels), (
            f"{tag_name} (multiple): prediction uses undefined labels: {labels}"
        )
        assert len(labels) >= 1, (
            f"{tag_name} (multiple): prediction should have at least 1 label, got {labels}"
        )

    for result in annotation["result"]:
        labels = result.get("value", {}).get(label_attr, [])
        assert all(label in declared_labels for label in labels), (
            f"{tag_name} (multiple): annotation uses undefined labels: {labels}"
        )
        assert len(labels) >= 1, (
            f"{tag_name} (multiple): annotation should have at least 1 label, got {labels}"
        )


def _tag_name(cls):
    field = cls.model_fields.get("tag")
    return field.default if field is not None else None


# Tags that own a `_label_attr_name` but whose value is NOT constrained against
# `self.labels` (free-form text/number/etc. or custom validation). They do not
# need a labels-aware `to_json_schema()` override and are skipped by the
# invariant test below. Adding a new free-form tag should extend this set.
_FREE_FORM_TAGS_WITHOUT_LABEL_ENUM = {
    "NumberTag",
    "DateTimeTag",
    "RatingTag",
    "TextAreaTag",
    "ReactCodeTag",
    "PairwiseTag",
    "RankerTag",
    "ChatMessageTag",
    "RelationsTag",
    "TaxonomyTag",  # has its own override + bespoke flat-path validation
}


_INVARIANT_LABEL_ARRAY_CONFIGS = {
    **LABEL_ARRAY_TAG_CONFIGS,
    "RectangleLabelsTag": """
    <View>
      <Image name="image" value="$image"/>
      <RectangleLabels name="label" toName="image">
        <Label value="Rect1"/>
        <Label value="Rect2"/>
      </RectangleLabels>
    </View>
    """,
    "LabelsTag": """
    <View>
      <Text name="text" value="$text"/>
      <Labels name="label" toName="text">
        <Label value="L1"/>
        <Label value="L2"/>
      </Labels>
    </View>
    """,
    "ChoicesTag": """
    <View>
      <Text name="text" value="$text"/>
      <Choices name="label" toName="text">
        <Choice value="C1"/>
        <Choice value="C2"/>
      </Choices>
    </View>
    """,
}


@pytest.mark.parametrize(
    "tag_cls_name,config",
    sorted(_INVARIANT_LABEL_ARRAY_CONFIGS.items()),
)
def test_every_labels_tag_produces_valid_sample_regions(tag_cls_name, config):
    """Invariant: every label-array control tag must produce valid sample regions.

    Mirrors the production code path in `LabelInterface._generate_sample_regions`,
    which is what blew up in Sentry as `ValueError: Using labels not defined in
    labeling config`. If this fails for a new tag, add a `to_json_schema()`
    override on it (see `_labels_json_schema` helper on `ControlTag` and existing
    overrides in control_tags.py for the pattern).
    """
    li = LabelInterface(config)
    control = li.get_control('label')
    schema = control.to_json_schema()
    assert schema != {"type": "string"}, (
        f"{tag_cls_name}.to_json_schema() returns the base default; "
        "JSF will produce a random string that fails label validation. "
        "Add a `to_json_schema()` override on this class."
    )
    li._generate_sample_regions()


def test_no_unaccounted_label_bearing_tags():
    """Invariant: every ControlTag subclass with `_label_attr_name` must be
    explicitly classified as either label-array (covered by the regression
    test above) or free-form (in `_FREE_FORM_TAGS_WITHOUT_LABEL_ENUM`).

    This guards against silently introducing a new label-array tag without a
    `to_json_schema()` override — which is exactly how BrushLabels and
    TimeSeriesLabels slipped past PLT-1114 and kept Sentry issue 7390937166
    firing in production.
    """
    accounted = set(_INVARIANT_LABEL_ARRAY_CONFIGS) | _FREE_FORM_TAGS_WITHOUT_LABEL_ENUM
    label_bearing = {
        cls.__name__
        for cls in _all_subclasses(ControlTag)
        # Only count classes that ship with the SDK; test fixtures may define
        # one-off subclasses (e.g. CustomChoicesTag) that pollute the registry.
        if cls.__module__ == "label_studio_sdk.label_interface.control_tags"
        and "_label_attr_name" in cls.__private_attributes__
        and cls.__private_attributes__["_label_attr_name"].default
    }
    missing = label_bearing - accounted
    assert not missing, (
        f"New label-bearing ControlTag subclass(es) detected: {sorted(missing)}. "
        "Add each to `_INVARIANT_LABEL_ARRAY_CONFIGS` (with a minimal XML config) "
        "if it is a label-array tag, or to `_FREE_FORM_TAGS_WITHOUT_LABEL_ENUM` "
        "if its value is not constrained against `self.labels`."
    )


def test_generate_url():
    """Quick check that each object tag generates the right data
    """

    def url_validator(url):
        assert url.startswith("https://") or url.startswith("http://")

    # TODO need to add other validators
    m = {
        "Audio": url_validator,
        "Image": url_validator,
        # "Table": None,
        "Text": url_validator,
        "Video": url_validator,
        # "HyperText": None,
        # "List": None,
        "Paragraphs": url_validator,
        # "TimeSeries": url_validator
    }

    for tag_name, validator in m.items():

        tag = Element(tag_name, {"name": "my_name", "value": "my_value"})
        inst = ObjectTag.parse_node(tag)

        res = inst.generate_example_value(mode="editor_preview", secure_mode=True)
        validator(res)
