import pytest
import json
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
            "required": []
        },
        {"sentiment": "Positive"},
        {"sentiment": "Positive"}
    ),
    # multiple choice
    (
        """
        <View>
          <Choices name="sentiment" toName="doc" choice="multiple">
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
                    "description": "Choices for doc",
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["Positive", "Negative", "Neutral"]
                    },
                    "uniqueItems": True,
                }
            },
            "required": []
        },
        {"sentiment": ["Positive", "Negative"]},
        {"sentiment": ["Positive", "Negative"]}
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
            "required": []
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
                    "oneOf": [
                        {"type": "string"},
                        {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    ],
                    "description": "Text or list of texts for document"
                }
            },
            "required": []
        },
        {"sentiment": "Positive"},
        {"sentiment": "Positive", "reasoning": None}
    ),
    # complex interface that includes all control tags
    (
        """
        <View>
          <Text name="txt" value="$text" />
          <Rating name="rating" toName="txt" maxRating="10" required="true"/>
          <DateTime name="date" toName="txt" />
          <Taxonomy name="taxonomy" toName="txt" required="true">
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
            "required": ["rating", "taxonomy"]
        },
        {"rating": 5, "date": "2024-01-01T00:00:00Z", "taxonomy": [["class B"], ["class A", "class A1"]], "number": 42.0, "pw": "left"},
        {"rating": 5, "date": datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc), "taxonomy": [["class B"], ["class A", "class A1"]], "number": 42.0, "pw": "left"}
    ),
    # textarea required
    (
        """
        <View>
          <Text name="document" value="$text" />
          <View>
            <Header value="Reasoning" />
            <TextArea name="reasoning" toName="document" required="true" />
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
                    "oneOf": [
                        {"type": "string"},
                        {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    ],
                    "description": "Text or list of texts for document"
                }
            },
            "required": ["reasoning"]
        },
        {"sentiment": "Positive", "reasoning": "Let's think step by step"},
        {"sentiment": "Positive", "reasoning": "Let's think step by step"}
    ),
    # add more tests for other control tags
    # ...
], ids=[
    "simple_choices",
    "multiple_choices",
    "ner",
    "classification_with_textarea",
    "complex_interface",
    "textarea_required",
    # specify ids for each test case
    # ...
])
def test_to_json_schema(config, expected_json_schema, input_arg, expected_result):
    interface = LabelInterface(config)
    
    # convert XML to JSON Schema
    json_schema = interface.to_json_schema()
    assert json_schema == expected_json_schema

    with json_schema_to_pydantic(json_schema) as ResponseModel:
        instance = ResponseModel(**input_arg)
        assert instance.model_dump() == expected_result



def process_json_schema(json_schema, input_arg, queue):
    with json_schema_to_pydantic(json_schema) as ResponseModel:
        instance = ResponseModel(**input_arg)
        queue.put(instance.model_dump())

def test_concurrent_json_schema_to_pydantic():
    import multiprocessing
    json_schema = {
        "type": "object",
        "properties": {
            "sentiment": {
                "type": "string",
                "description": "Choices for doc",
                "enum": ["Positive", "Negative", "Neutral"],
            }
        },
        "required": ["sentiment"]
    }
    input_arg1 = {"sentiment": "Positive"}
    input_arg2 = {"sentiment": "Negative"}
    
    queue = multiprocessing.Queue()
    
    p1 = multiprocessing.Process(target=process_json_schema, args=(json_schema, input_arg1, queue))
    p2 = multiprocessing.Process(target=process_json_schema, args=(json_schema, input_arg2, queue))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
    
    results = [queue.get() for _ in range(2)]
    
    assert {"sentiment": "Positive"} in results
    assert {"sentiment": "Negative"} in results
    assert len(results) == 2


def process_json_schema_threaded(json_schema, input_arg, results, index):
    with json_schema_to_pydantic(json_schema) as ResponseModel:
        instance = ResponseModel(**input_arg)
        results[index] = instance.model_dump()

def test_concurrent_json_schema_to_pydantic_threaded():
    import threading
    import time
    
    json_schema = {
        "type": "object",
        "properties": {
            "sentiment": {
                "type": "string",
                "description": "Choices for doc",
                "enum": ["Positive", "Negative", "Neutral"],
            }
        },
        "required": ["sentiment"]
    }
    input_args = [
        {"sentiment": "Positive"},
        {"sentiment": "Negative"},
        {"sentiment": "Neutral"},
        {"sentiment": "Positive"}
    ]
    
    results = [None] * len(input_args)
    threads = []

    # Create and start threads
    for i, input_arg in enumerate(input_args):
        thread = threading.Thread(target=process_json_schema_threaded, args=(json_schema, input_arg, results, i))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify results
    assert {"sentiment": "Positive"} in results
    assert {"sentiment": "Negative"} in results
    assert {"sentiment": "Neutral"} in results
    assert results.count({"sentiment": "Positive"}) == 2
    assert len(results) == 4
    assert None not in results

    # Verify thread safety by running multiple times
    for _ in range(10):
        results = [None] * len(input_args)
        threads = []

        start_time = time.time()
        for i, input_arg in enumerate(input_args):
            thread = threading.Thread(target=process_json_schema_threaded, args=(json_schema, input_arg, results, i))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        end_time = time.time()

        assert set(result["sentiment"] for result in results) == set(["Positive", "Negative", "Neutral"])
        assert results.count({"sentiment": "Positive"}) == 2
        assert len(results) == 4
        assert None not in results

        # Check if execution time is reasonable (adjust as needed)
        assert end_time - start_time < 1.0, f"Execution took too long: {end_time - start_time} seconds"