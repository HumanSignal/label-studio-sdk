import json
import types
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from datamodel_code_generator import InputFileType, generate, DataModelType, LiteralType
from pydantic import BaseModel
from io import StringIO
from contextlib import contextmanager


@contextmanager
def json_schema_to_pydantic(json_schema: dict, class_name: str = 'MyModel') -> type[BaseModel]:
    """
    Convert a JSON schema to a Pydantic model and provide it as a context manager.

    Args:
        json_schema (dict): The JSON schema to convert.
        class_name (str, optional): The name of the generated Pydantic class. Defaults to 'MyModel'.

    Example:
        ```python
        example_schema = {
            "type": "object",
            "properties": {
                "sentiment": {
                    "type": "string",
                    "description": "Sentiment of the text",
                    "enum": ["Positive", "Negative", "Neutral"],
                }
            },
            "required": ["sentiment"]
        }
        with json_schema_to_pydantic(example_schema) as ResponseModel:
            instance = ResponseModel(sentiment='Positive')
            print(instance.model_dump())
        ```
    """
    json_schema_str = json.dumps(json_schema)

    with TemporaryDirectory() as temp_dir:
        temp_file = Path(temp_dir) / "schema.py"
        
        generate(
            json_schema_str,
            input_file_type=InputFileType.JsonSchema,
            input_filename="schema.json",
            output=temp_file,
            output_model_type=DataModelType.PydanticV2BaseModel,
            enum_field_as_literal=LiteralType.All,
            class_name=class_name
        )
        
        model_code = temp_file.read_text()

    mod = types.ModuleType('dynamic_module')
    exec(model_code, mod.__dict__)

    model_class = getattr(mod, class_name)
    
    try:
        sys.modules['dynamic_module'] = mod
        yield model_class
    finally:
        if 'dynamic_module' in sys.modules:
            del sys.modules['dynamic_module']
