import pytest
from . import configs as c
from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.label_interface.object_tags import ObjectTag
from lxml.etree import Element

# Configs for the nine label-array control tags in scope for hp-wgxy
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
}


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
