import pytest
from datetime import datetime, timezone
from label_studio_sdk.label_interface.interface import LabelInterface
from label_studio_sdk.label_interface.control_tags import ControlTag
from label_studio_sdk._extensions.label_studio_tools.core.utils.json_schema import json_schema_to_pydantic



@pytest.mark.parametrize("config, expected_json_schema, input_arg, expected_result", [
    # simple choices
    (
        """
        <View>
          <Choices name="sentiment" toName="doc">
            <Choice value="Positive" />
            <Choice value="Negative" />
            <Choice value="Neutral" />
          </Choices>
          <Text name="doc" value="$text" />
        </View>
        """,
        {
            "type": "object",
            "properties": {
                "sentiment": {
                    "type": "string",
                    "description": "Choices for doc",
                    "enum": ["Positive", "Negative", "Neutral"],
                }
            },
            "required": ["sentiment"]
        },
        {"sentiment": "Positive"},
        {"sentiment": "Positive"}
    ),
    # ner
    (
        """
        <View>
          <View className="row">
          <Text name="txt" value="$text" />
          </View>
          <Labels name="entities" toName="txt">
            <Label value="PERSON" />
            <Label value="ORG" />
            <Label value="LOC" />
          </Labels>
        </View>
        """,
        {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "description": "Labels and span indices for txt",
                    "items": {
                        "type": "object",
                        "required": ["start", "end", "labels"],
                        "properties": {
                            "start": {
                                "type": "integer",
                                "minimum": 0
                            },
                            "end": {
                                "type": "integer",
                                "minimum": 0
                            },
                            "labels": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["PERSON", "ORG", "LOC"]
                                }
                            },
                            "text": {
                                "type": "string"
                            }
                        }
                    }
                }
            },
            "required": ["entities"]
        },
        {"entities": [{"start": 0, "end": 1, "labels": ["PERSON"], "text": "John"}]},
        {"entities": [{"start": 0, "end": 1, "labels": ["PERSON"], "text": "John"}]}
    ),
    # classification with textarea  
    (
        """
        <View>
          <Text name="document" value="$text" />
          <View>
            <Header value="Reasoning" />
            <TextArea name="reasoning" toName="document" />
          </View>
          <View>
            <Header value="Classification" />
            <Choices name="sentiment" toName="document">
              <Choice value="Positive" />
            <Choice value="Negative" />
              <Choice value="Neutral" />
            </Choices>
          </View>
        </View>
        """,
        {
            "type": "object",
            "properties": {
                "sentiment": {
                    "type": "string",
                    "description": "Choices for document",
                    "enum": ["Positive", "Negative", "Neutral"],
                },
                "reasoning": {
                    "type": "string",
                    "description": "Text for document"
                }
            },
            "required": ["reasoning", "sentiment"]
        },
        {"sentiment": "Positive", "reasoning": "Let's think step by step"},
        {"sentiment": "Positive", "reasoning": "Let's think step by step"}
    ),
    # complex interface that includes all control tags
    (
        """
        <View>
          <Text name="txt" value="$text" />
          <Rating name="rating" toName="txt" maxRating="10" />
          <DateTime name="date" toName="txt" />
          <Taxonomy name="taxonomy" toName="txt" >
          <Choice value="class A">
           <Choice value="class A1"/>
           <Choice value="class A2"/>
           </Choice>
          <Choice value="class B"/>
          </Taxonomy>
          <Number name="number" toName="txt" min="0" max="100"/>

          <Text name="txt2" value="$text" />
            <Pairwise name="pw" leftClass="$text1_label" rightClass="$text2_label" toName="txt,txt2" />
        </View>
        """,
        {
            "type": "object",
            "properties": {
                "rating": {
                    "type": "integer",
                    "description": "Rating for txt (0 to 10)",
                    "minimum": 0,
                    "maximum": 10
                },
                "date": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Date and time for txt"
                },
                "taxonomy": {
                    "type": "array",
                    "description": "Taxonomy for txt. Each item is a path from root to selected node.",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["class A", "class A1", "class A2", "class B"]
                        }
                    }
                },
                "number": {
                    "type": "number",
                    "description": "Number for txt",
                    "minimum": 0.0,
                    "maximum": 100.0
                },
                "pw": {
                    "type": "string",
                    "description": "Pairwise selection between txt (left) and txt2 (right)",
                    "enum": ["left", "right"]
                }
            },
            "required": ["rating", "date", "taxonomy", "number", "pw"]
        },
        {"rating": 5, "date": "2024-01-01T00:00:00Z", "taxonomy": [["class B"], ["class A", "class A1"]], "number": 42.0, "pw": "left"},
        {"rating": 5, "date": datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc), "taxonomy": [["class B"], ["class A", "class A1"]], "number": 42.0, "pw": "left"}
    ),
    # add more tests for other control tags
    # ...
], ids=[
    "simple_choices",
    "ner",
    "classification_with_textarea",
    "complex_interface"
    # specify ids for each test case
    # ...
])
def test_to_json_schema(config, expected_json_schema, input_arg, expected_result):
    interface = LabelInterface(config)
    
    # convert XML to JSON Schema
    json_schema = interface.to_json_schema()
    assert json_schema == expected_json_schema

    # convert JSON Schema to Pydantic
    with json_schema_to_pydantic(json_schema) as ResponseModel:
        instance = ResponseModel(**input_arg)
        assert instance.model_dump() == expected_result