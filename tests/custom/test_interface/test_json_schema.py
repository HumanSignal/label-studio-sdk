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
                                "oneOf": [
                                    {"type": "integer", "minimum": 0},
                                    {"type": "number", "minimum": 0}
                                ]
                            },
                            "end": {
                                "oneOf": [
                                    {"type": "integer", "minimum": 0},
                                    {"type": "number", "minimum": 0}
                                ]
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
    # custom interface with simple comma-delimited outputs
    (
        """
        <View>
          <CustomInterface name="my_app" toName="my_app" data="$my_data" outputs="field1,field2,field3" />
        </View>
        """,
        {
            "type": "object",
            "properties": {
                "my_app": {
                    "type": "object",
                    "properties": {
                        "field1": {"type": "string"},
                        "field2": {"type": "string"},
                        "field3": {"type": "string"},
                    }
                }
            },
            "required": []
        },
        {"my_app": {"field1": "value1", "field2": "value2", "field3": "value3"}},
        {"my_app": {"field1": "value1", "field2": "value2", "field3": "value3"}}
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
    "custom_interface",
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


@pytest.mark.parametrize("outputs_attr, expected_properties, sample_input", [
    # Strategy 1: Delimited list - comma separated
    (
        "field1, field2, field3",
        {
            "field1": {"type": "string"},
            "field2": {"type": "string"},
            "field3": {"type": "string"},
        },
        {"field1": "a", "field2": "b", "field3": "c"}
    ),
    # Strategy 1: Delimited list - pipe separated
    (
        "name|email|phone",
        {
            "name": {"type": "string"},
            "email": {"type": "string"},
            "phone": {"type": "string"},
        },
        {"name": "John", "email": "john@example.com", "phone": "123"}
    ),
    # Strategy 1: Delimited list - semicolon separated
    (
        "a;b;c",
        {
            "a": {"type": "string"},
            "b": {"type": "string"},
            "c": {"type": "string"},
        },
        {"a": "1", "b": "2", "c": "3"}
    ),
    # Strategy 2: JSON schema - properties only (quotes escaped for XML)
    (
        '{&quot;score&quot;: {&quot;type&quot;: &quot;number&quot;}, &quot;comment&quot;: {&quot;type&quot;: &quot;string&quot;}}',
        {
            "score": {"type": "number"},
            "comment": {"type": "string"},
        },
        {"score": 42.5, "comment": "great"}
    ),
    # Strategy 2: JSON schema - complete schema (quotes escaped for XML)
    (
        '{&quot;type&quot;: &quot;object&quot;, &quot;properties&quot;: {&quot;value&quot;: {&quot;type&quot;: &quot;integer&quot;, &quot;minimum&quot;: 0}}}',
        {"value": {"type": "integer", "minimum": 0}},
        {"value": 10}
    ),
    # List of objects
    (
        '''
        {
        &quot;type&quot;: &quot;array&quot;,
        &quot;items&quot;: {
            &quot;type&quot;: &quot;object&quot;,
            &quot;properties&quot;: {
            &quot;index&quot;: {
                &quot;type&quot;: &quot;string&quot;
            },
            &quot;category&quot;: {
                &quot;type&quot;: &quot;string&quot;,
                &quot;enum&quot;: [
                &quot;fraud&quot;,
                &quot;not_fraud&quot;
                ]
            },
            &quot;groupNames&quot;: {
                &quot;type&quot;: &quot;string&quot;
            }
            },
            &quot;required&quot;: [&quot;index&quot;, &quot;category&quot;, &quot;groupNames&quot;]
        }
        }''',
        [{
            "index": {"type": "string"},
            "category": {"type": "string", "enum": ["fraud", "not_fraud"]},
            "groupNames": {"type": "string"}
        }],
        [{"index": "1", "category": "fraud", "groupNames": "group1"}]
    ),
    # Strategy 3: Type alias - choices
    (
        "sentiment:choices(positive, negative, neutral)",
        {
            "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
        },
        {"sentiment": "positive"}
    ),
    # Strategy 3: Type alias - multichoices
    (
        "tags:multichoices(urgent, review, done)",
        {
            "tags": {"type": "array", "items": {"type": "string", "enum": ["urgent", "review", "done"]}},
        },
        {"tags": ["urgent", "review"]}
    ),
    # Strategy 3: Type alias - number with min/max
    (
        "score:number(0, 100)",
        {
            "score": {"type": "number", "minimum": 0.0, "maximum": 100.0},
        },
        {"score": 75.5}
    ),
    # Strategy 3: Type alias - rating
    (
        "stars:rating(5)",
        {
            "stars": {"type": "integer", "minimum": 1, "maximum": 5},
        },
        {"stars": 4}
    ),
    # Mixed: delimited list with type aliases
    (
        "name, sentiment:choices(good, bad), score:number(1, 10), tags:multichoices(a, b)",
        {
            "name": {"type": "string"},
            "sentiment": {"type": "string", "enum": ["good", "bad"]},
            "score": {"type": "number", "minimum": 1.0, "maximum": 10.0},
            "tags": {"type": "array", "items": {"type": "string", "enum": ["a", "b"]}},
        },
        {"name": "test", "sentiment": "good", "score": 5.0, "tags": ["a"]}
    ),
    # Mixed: pipe-delimited with rating
    (
        "comment|quality:rating(10)",
        {
            "comment": {"type": "string"},
            "quality": {"type": "integer", "minimum": 1, "maximum": 10},
        },
        {"comment": "nice", "quality": 8}
    ),
], ids=[
    "comma_delimited",
    "pipe_delimited",
    "semicolon_delimited",
    "json_properties",
    "json_complete_schema",
    "json_schema_list_of_objects",
    "choices_alias",
    "multichoices_alias",
    "number_alias",
    "rating_alias",
    "mixed_delimited_with_aliases",
    "pipe_with_rating",
])
def test_custom_interface_outputs_parsing(outputs_attr, expected_properties, sample_input):
    """Test various parsing strategies for CustomInterface outputs attribute."""
    config = f'''
    <View>
      <CustomInterface name="result" toName="result" outputs="{outputs_attr}" />
    </View>
    '''
    interface = LabelInterface(config)
    json_schema = interface.to_json_schema()
    
    # Handle case where expected_properties might be a list (for array schemas)
    if isinstance(expected_properties, list):
        expected_schema = {
            "type": "object",
            "properties": {
                "result": {
                    "type": "array",
                    "items": {
                        "type": "object", 
                        "properties": expected_properties[0] if expected_properties else {},
                        "required": list(expected_properties[0].keys()) if expected_properties else []
                    }
                }
            },
            "required": []
        }
    else:
        expected_schema = {
            "type": "object",
            "properties": {
                "result": {
                    "type": "object",
                    "properties": expected_properties
                }
            },
            "required": []
        }
    assert json_schema == expected_schema
    
    # Validate that the schema works with pydantic
    with json_schema_to_pydantic(json_schema) as ResponseModel:
        instance = ResponseModel(result=sample_input)
        assert instance.model_dump()["result"] == sample_input
