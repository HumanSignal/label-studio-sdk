import json
import types
import sys
import functools
from typing import Type, Dict, Any, Tuple, Generator
from pathlib import Path
from tempfile import TemporaryDirectory
from datamodel_code_generator import InputFileType, generate, DataModelType, LiteralType
from pydantic import BaseModel
from io import StringIO
from contextlib import contextmanager


@functools.lru_cache(maxsize=128)
def _generate_model_code(json_schema_str: str, class_name: str = 'MyModel') -> str:
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
        
        return temp_file.read_text()

@contextmanager
def json_schema_to_pydantic(json_schema: dict, class_name: str = 'MyModel') -> Generator[Type[BaseModel], None, None]:
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
    # Convert the JSON schema dictionary to a JSON string
    json_schema_str = json.dumps(json_schema)
    
    # Generate Pydantic model code from the JSON schema string
    model_code: str = _generate_model_code(json_schema_str, class_name)
    
    # Create a unique module name using the id of the JSON schema string
    module_name = f'dynamic_module_{id(json_schema_str)}'
    
    # Create a new module object with the unique name and execute the generated model code in the context of the new module
    mod = types.ModuleType(module_name)
    exec(model_code, mod.__dict__)
    model_class = getattr(mod, class_name)
    
    try:
        # Add the new module to sys.modules to make it importable
        # This is necessary to avoid Pydantic errors related to undefined models
        sys.modules[module_name] = mod
        yield model_class
    finally:
        if module_name in sys.modules:
            del sys.modules[module_name]
        