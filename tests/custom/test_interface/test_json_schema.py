import pytest
from label_studio_sdk.label_interface.interface import LabelInterface
from label_studio_sdk.label_interface.control_tags import ControlTag
from label_studio_sdk._extensions.label_studio_tools.core.utils.json_schema import json_schema_to_pydantic

def test_to_json_schema():
    # Sample XML configuration string
    config = """
    <View>
      <Choices name="sentiment" toName="txt">
        <Choice value="Positive" />
        <Choice value="Negative" />
        <Choice value="Neutral" />
      </Choices>
      <Text name="txt" value="$text" />
    </View>
    """

    expected_json_schema = {
        "type": "object",
        "properties": {
            "sentiment": {
                "type": "string",
                "description": "sentiment",
            }
        },
        "required": ["sentiment"]
    }

    interface = LabelInterface(config)

    # convert XML to JSON Schema
    json_schema = interface.to_json_schema()
    assert json_schema == expected_json_schema

    # convert JSON Schema to Pydantic
    with json_schema_to_pydantic(json_schema) as ResponseModel:
        instance = ResponseModel(sentiment='Positive')
        assert instance.model_dump() == {'sentiment': 'Positive'}
