"""
"""

import os
import copy
import logging
import re
import json
import jsonschema

from functools import cached_property
from typing import Dict, Optional, List, Tuple, Any, Callable, Union
from pydantic import BaseModel


# from typing import Dict, Optional, List, Tuple, Any
from collections import defaultdict, OrderedDict
from lxml import etree
import xmljson
from jsf import JSF

from label_studio_sdk._legacy.exceptions import (
    LSConfigParseException,
    LabelStudioXMLSyntaxErrorSentryIgnored,
    LabelStudioValidationErrorSentryIgnored,
)

from .base import LabelStudioTag
from .control_tags import (
    ControlTag,
    ChoicesTag,
    LabelsTag,
)
from .object_tags import ObjectTag
from .label_tags import LabelTag
from .objects import AnnotationValue, TaskValue, PredictionValue, Region
from . import create as CE

logger = logging.getLogger(__name__)


dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(dir_path, "..", "_legacy", "schema", "label_config_schema.json")

with open(file_path) as f:
    _LABEL_CONFIG_SCHEMA_DATA = json.load(f)

_LABEL_TAGS = {"Label", "Choice", "Relation"}

_DIR_APP_NAME = "label-studio"
_VIDEO_TRACKING_TAGS = {"videorectangle"}

RESULT_KEY = "result"

############ core/label_config.py


def merge_labels_counters(dict1, dict2):
    """
    Merge two dictionaries with nested dictionary values into a single dictionary.

    Args:
        dict1 (dict): The first dictionary to merge.
        dict2 (dict): The second dictionary to merge.

    Returns:
        dict: A new dictionary with the merged nested dictionaries.

    Example:
        dict1 = {'sentiment': {'Negative': 1, 'Positive': 1}}
        dict2 = {'sentiment': {'Positive': 2, 'Neutral': 1}}
        result_dict = merge_nested_dicts(dict1, dict2)
        # {'sentiment': {'Negative': 1, 'Positive': 3, 'Neutral': 1}}
    """
    result_dict = {}

    # iterate over keys in both dictionaries
    for key in set(dict1.keys()) | set(dict2.keys()):
        # add the corresponding values if they exist in both dictionaries
        value = {}
        if key in dict1:
            value.update(dict1[key])
        if key in dict2:
            for subkey in dict2[key]:
                value[subkey] = value.get(subkey, 0) + dict2[key][subkey]
        # add the key-value pair to the result dictionary
        result_dict[key] = value

    return result_dict


def _fix_choices(config):
    """
    workaround for single choice
    https://github.com/heartexlabs/label-studio/issues/1259
    """
    if "Choices" in config:
        # for single Choices tag in View
        if "Choice" in config["Choices"] and not isinstance(
            config["Choices"]["Choice"], list
        ):
            config["Choices"]["Choice"] = [config["Choices"]["Choice"]]
        # for several Choices tags in View
        elif isinstance(config["Choices"], list) and all(
            "Choice" in tag_choices for tag_choices in config["Choices"]
        ):
            for n in range(len(config["Choices"])):
                # check that Choices tag has only 1 choice
                if not isinstance(config["Choices"][n]["Choice"], list):
                    config["Choices"][n]["Choice"] = [config["Choices"][n]["Choice"]]
    if "View" in config:
        if isinstance(config["View"], OrderedDict):
            config["View"] = _fix_choices(config["View"])
        else:
            config["View"] = [_fix_choices(view) for view in config["View"]]
    return config


def get_annotation_tuple(from_name, to_name, type):
    if isinstance(to_name, list):
        to_name = ",".join(to_name)
    return "|".join([from_name, to_name, type.lower()])


def get_all_control_tag_tuples(label_config):
    # "chc|text|choices"
    outputs = parse_config(label_config)
    out = []
    for control_name, info in outputs.items():
        out.append(get_annotation_tuple(control_name, info["to_name"], info["type"]))
    return out


def get_all_types(label_config):
    """
    Get all types from label_config
    """
    outputs = parse_config(label_config)
    out = []
    for control_name, info in outputs.items():
        out.append(info["type"].lower())
    return out


def display_count(count: int, type: str) -> Optional[str]:
    """Helper for displaying pluralized sources of validation errors,
    eg "1 draft" or "3 annotations"
    """
    if not count:
        return None

    return f'{count} {type}{"s" if count > 1 else ""}'


######################


class LabelInterface:
    """The LabelInterface class serves as an interface to parse and
    validate labeling configurations, annotations, and predictions
    within the Label Studio ecosystem.

    It is designed to be compatible at the data structure level with
    an existing parser widely used within the Label Studio ecosystem.
    This ensures that it works seamlessly with most of the existing functions,
    either by directly supporting them or by offering re-implemented versions
    through the new interface.

    Moreover, the parser adds value by offering functionality to
    validate predictions and annotations against the specified
    labeling configuration. Below is a simple example of how to use
    the new API:

    ```python
    from label_studio_sdk.label_interface import LabelInterface

    config = "<View><Text name='txt' value='$val' /><Choices name='chc' toName='txt'><Choice value='one'/> <Choice value='two'/></Choices></View>"

    li = LabelInterface(config)
    region = li.get_tag("chc").label("one")

    # returns a JSON representing a Label Studio region
    region.as_json()

    # returns True
    li.validate_prediction({
      "model_version": "0.0.1",
      "score": 0.90,
      "result": [{
          "from_name": "chc",
          "to_name": "txt",
          "type": "choices",
          "value": { "choices": ["one"] }
      }]
    })
    ```
    """

    @classmethod
    def create(cls, tags, mapping=None, title=None, style=None, pretty=True, *args, **kwargs):
        """ Simple way of create UI config, it helps you not to thing much about the name/toName mapping

        LabelInterface.create_simple({
          "txt": "Text",
          "chc": choices("positive", "negative")
        })
        """
        tuples = CE.convert_tags_description(tags, mapping=mapping)

        if isinstance(title, str):
            tuples = (("Header", { "value": title }, {}),) + tuples

        # in case we have either title or style, then we can iterate
        # through the tuples and modify the tree
        if isinstance(title, dict) or isinstance(style, dict):
            new_tuples = []
            for t in tuples:
                tag, attributes, children = t
                name = attributes.get("name", None)

                # prepend Header tag to the list
                if isinstance(title, dict) and name in title:
                    title_tag = ("Header", { "value": title.get(name) }, {})
                    new_tuples.append(title_tag)

                # modify the style of the element by wrapping it into
                # a View with style
                if isinstance(style, dict) and name in style:
                    parent_tag = ("View", { "style": style.get(name) }, (t,))
                    new_tuples.append(parent_tag)
                else:
                    new_tuples.append(t)

            tuples = new_tuples
        
        tree = CE.tree_from_tuples(*tuples)
        
        return CE.tree_to_string(tree, pretty=pretty)

    
    @classmethod
    def create_instance(cls, *args, **kwargs):
        """Create instance is a shortcut to create a config and then
        parse it right away returning the LabelInterface object

        ```
        li = LabelInterface.create_instance({ "txt": "Text", "lbl": labels(("person", "org")) })
        lbl = li.get_control("lbl")
        reg = lbl.label("person", start=0, end=10)
        ```
        
        The above returns a region that could be serialized to Label
        Studio JSON format and uploaded to Label Studio

        """
        config = cls.create(*args, **kwargs)
        return cls(config=config, **kwargs)

    def __init__(self, config: str, tags_mapping=None, *args, **kwargs):
        """
        Initialize a LabelInterface instance using a config string.

        Args:
          config (str): Configuration string.
          tags_mapping: Provide your own implementation of any tag, this is helpful in cases where you want to override one of the control tags, and have your custom .label() method implemented.

        The configuration string should be formatted as follows:

        ```
        <View>
          <Choices name="sentiment" toName="txt">
            <Choice value="Positive" />
            <Choice value="Negative" />
            <Choice value="Neutral" />
          </Choices>
          <Text name="txt" value="$text" />
        </View>
        ```
        This method will extract the predefined task from the configuration and 
        parse the controls, objects, and labels used in it.
        """
        self.task_loaded = False
        
        self._config = config
        self._tags_mapping = tags_mapping
        
        # extract predefined task from the config
        _task_data, _ann, _pred = LabelInterface.get_task_from_labeling_config(config)
        self._sample_config_task = _task_data
        self._sample_config_ann = _ann
        self._sample_config_pred = _pred

        controls, objects, labels, tree = self.parse(config)
        controls = self._link_controls(controls, objects, labels)

        # list of control tags that this config has
        self._control_tags = set(controls.keys())
        self._object_tags = set(objects.keys())
        # self._label_names = set(labels.keys())

        self._controls = controls
        self._objects = objects
        self._labels = labels
        self._tree = tree

    def create_regions(self, data: Dict[str, Union[str, Dict, List[str], List[Dict]]]) -> List[Region]:
        """
        Takes raw data representation and maps keys to control tag names.
        If name is not found, it will be skipped

        Args:
            data (Dict): Raw data representation. Example: {"choices_name": "Positive", "labels_name": [{"start": 0, "end": 10, "label": "person"}]}
            raise_if_control_not_found (bool): Raise an exception if control tag is not found.
        """
        regions = []
        for control_tag_name, payload in data.items():
            
            if payload is None:
                logger.warning(
                    f"Payload for control tag '{control_tag_name}' is None: "
                    "it can be ok if this payload is autogenerated by LLMs - "
                    "try to adjust the prompt to generate valid payloads. "
                    "Otherwise, it can signify an error")
                continue
            
            if control_tag_name not in self._controls:
                logger.info(f"Control tag '{control_tag_name}' not found in the config")
                continue

            control = self._controls[control_tag_name]
            # TODO: I don't really like this part, looks like a workaround
            # 1. we should allow control.label to process custom payload outside of those strictly containing "label"
            # 2. we should be less open regarding the payload type and defining the strict typing elsewhere,
            # but likely that requires rewriting of how ControlTag.label() is working now
            if isinstance(payload, (str, int, float)):
                payload = {'label': payload}
            elif isinstance(payload, list):
                if len(payload) > 0:
                    if isinstance(payload[0], str):
                        payload = {'label': payload}
                    else:
                        pass

            if isinstance(payload, Dict):
                payload = [payload]

            for item in payload:
                regions.append(control.label(**item))

        return regions

    @property
    def config(self):
        """Returns the XML configuration string"""
        return self._config

    @property
    def controls(self):
        """Returns list of control tags"""
        return self._controls and self._controls.values()

    @property
    def objects(self):
        """Returns list of object tags"""
        return self._objects and self._objects.values()

    @property
    def labels(self):
        """Returns list of label tags"""
        return self._labels and self._labels.values()

    def _link_controls(self, controls: Dict, objects: Dict, labels: Dict) -> Dict:
        """ """
        for name, tag in controls.items():
            inputs = []
            for object_tag_name in tag.to_name:
                if object_tag_name not in objects:
                    # logger.info(
                    #     f'to_name={object_tag_name} is specified for output tag name={name}, '
                    #     'but we can\'t find it among input tags'
                    # )
                    continue

                inputs.append(objects[object_tag_name])

            tag.set_objects(inputs)
            tag.set_labels(list(labels[name]))
            tag.set_labels_attrs(labels[name])

        return controls

    def _get_tag(self, name, tag_store):
        """ """
        if name is not None:
            if name not in tag_store:
                raise Exception(
                    f"Name {name} is not found, available names: {tag_store.keys()}"
                )
            else:
                return tag_store[name]

        if tag_store and len(tag_store.keys()) > 1:
            raise Exception("Multiple object tags connected, you should specify name")

        return list(tag_store.values())[0]

    def get_tag(self, name):
        """Method to retrieve the tag object by its name from the current instance.

        The method checks if the tag with the provided name exists in
        either `_controls` or `_objects` attributes of the current
        instance.  If a match is found, it returns the tag. If the tag
        is not found an exception is raised.

        Args:
            name (str): Name of the tag to be retrieved.

        Returns:
            object: The tag object if it exists in either `_controls` or `_objects`.

        Raises:
            Exception: If the tag with the given name does not exist in both `_controls` and `_objects`.

        """
        if name in self._controls:
            return self._controls[name]

        if name in self._objects:
            return self._objects[name]

        raise Exception(f"Tag with name {name} not found")

    def get_object(self, name=None):
        """Retrieves the object with the given name from `_objects`.

        This utilizes the `_get_tag` method to obtain the named object.

        Args:
            name (str, optional): The name of the object to be retrieved from `_objects`.

        Returns: object: The corresponding object if it exists in
            `_objects`.

        """
        return self._get_tag(name, self._objects)

    def get_output(self, name=None):
        """Provides an alias for the `get_control` method."""
        return self.get_control(name)

    def get_control(self, name=None):
        """Retrieves the control tag that the control tag maps to.

        This uses the `_get_tag` method to obtain the named control.

        Args:
            name (str, optional): The name of the control to be retrieved.

        Returns: object: The corresponding control if it exists in
            `_controls`.

        """
        return self._get_tag(name, self._controls)

    def find_tags_by_class(self, tag_class) -> List:
        """Finds tags by their class type.

        The function looks into both `self.objects` and
        `self.controls` to find tags that are instances of the
        provided class(es)

        Args:
            tag_class (class or list of classes): The class type(s) of the tags to be found.

        Returns:
            list: A list of tags that are instances of the provided `tag_class`(es).

        """
        lst = list(self.objects) + list(self.controls)
        tag_classes = [tag_class] if not isinstance(tag_class, list) else tag_class

        return [tag for tag in lst for cls in tag_classes if isinstance(tag, cls)]

    def find_tags(
        self, tag_type: Optional[str] = None, match_fn: Optional[Callable] = None
    ) -> List:
        """Finds tags that match the given function in the entire parsed tree.

        This function searches through both `objects` and `controls`
        based on `tag_type`, and applies the `match_fn` (if provided)
        to filter matching tags.

        Args:
            tag_type (str, optional): The type of tags to be
                searched. Categories include 'objects', 'controls',
                'inputs' (alias for 'objects'), 'outputs' (alias for
                'controls'). If not specified, searches both 'objects'
                and 'controls'.
            match_fn (Callable, optional): A function that takes a tag
                as an input and returns a boolean value indicating
                whether the tag matches the required condition.

        Returns: list: A list of tags that match the given type and
        satisfy `match_fn`.

        """
        tag_types = {
            "objects": self.objects,
            "controls": self.controls,
            # aliases
            "inputs": self.objects,
            "outputs": self.controls,
        }

        lst = tag_types.get(tag_type, list(self.objects) + list(self.controls))

        if match_fn is not None:
            lst = list(filter(match_fn, lst))

        return lst
    
    @cached_property
    def ner_tags(self):
        return self.find_tags('controls', lambda t: t.tag.lower() in ('labels', 'hypertextlabels'))
    
    @cached_property
    def image_tags(self):
        return self.find_tags('objects', lambda t: t.tag.lower() == 'image')
    
    @cached_property
    def pdf_tags(self):
        return self.find_tags('objects', lambda t: t.tag.lower() == 'pdf')


    def load_task(self, task):
        """Loads a task and substitutes the value in each object tag
        with actual data from the task, returning a copy of the
        LabelConfig object.

        If the `value` field in an object tag is designed to take
        variable input (i.e., `value_is_variable` is True), the
        function replaces this value with the corresponding value from
        the task dictionary.

        Args:
            task (dict): Dictionary representing the task, where
            each key-value pair denotes an attribute-value of the
            task.

        Returns:
            LabelInterface: A deep copy of the current LabelIntreface
            instance with the object tags' value fields populated with
            data from the task.

        """
        tree = copy.deepcopy(self)
        tree.task_loaded = True
        
        for obj in tree.objects:
            if obj.value_is_variable and obj.value_name in task:
                obj.value = task.get(obj.value_name)

        return tree
    
    def to_json_schema(self):
        """
        Converts the current LabelInterface instance into a JSON Schema.

        Returns:
            dict: A dictionary representing the JSON Schema.
        """
        required_outputs = [
            name for name, control in self._controls.items()
            if control.is_output_required
        ]
        return {
            "type": "object",
            "properties": {
                name: control.to_json_schema() for name, control in self._controls.items()
            },
            "required": required_outputs
        }

    def parse(self, config_string: str) -> Tuple[Dict, Dict, Dict, etree._Element]:
        """Parses the received configuration string into dictionaries
        of ControlTags, ObjectTags, and Labels, along with an XML tree
        of the configuration.

        Args:
            config_string (str): the configuration string to be parsed.

        Returns:
            Tuple of:
            - Dictionary where keys are control tag names and values are ControlTag instances.
            - Dictionary where keys are object tag names and values are ObjectTag instances.
            - Dictionary of dictionaries where primary keys are label parent names
              and secondary keys are label values and values are LabelTag instances.
            - An XML tree of the configuration.
        """
        try:
            xml_tree = etree.fromstring(config_string)
        except etree.XMLSyntaxError as e:
            raise LabelStudioXMLSyntaxErrorSentryIgnored(str(e))

        objects, controls, labels = {}, {}, defaultdict(dict)

        variables = []

        for tag in xml_tree.iter():
            if tag.attrib and "indexFlag" in tag.attrib:
                variables.append(tag.attrib["indexFlag"])

            if ControlTag.validate_node(tag):
                controls[tag.attrib["name"]] = ControlTag.parse_node(tag, tags_mapping=self._tags_mapping)

            elif ObjectTag.validate_node(tag):
                objects[tag.attrib["name"]] = ObjectTag.parse_node(tag, tags_mapping=self._tags_mapping)

            elif LabelTag.validate_node(tag):
                lb = LabelTag.parse_node(tag, controls)
                # This case is hit when Label tag is missing `value` and `alias`
                # For now we will skip that Label, but in future might want to raise an error
                if lb:
                    labels[lb.parent_name][lb.value] = lb

        return controls, objects, labels, xml_tree

    @classmethod
    def parse_config_to_json(cls, config_string):
        """ """
        try:
            xml = etree.fromstring(config_string)
        except TypeError:
            raise etree.ParseError("can only parse strings")
        if xml is None:
            raise etree.ParseError("xml is empty or incorrect")

        config = xmljson.badgerfish.data(xml)
        config = _fix_choices(config)

        return config

    def _schema_validation(self, config_string):
        """ """
        try:
            config = LabelInterface.parse_config_to_json(config_string)
            jsonschema.validate(config, _LABEL_CONFIG_SCHEMA_DATA)
        except (etree.ParseError, ValueError) as exc:
            raise LabelStudioValidationErrorSentryIgnored(str(exc))
        except jsonschema.exceptions.ValidationError as exc:
            error_message = exc.context[-1].message if len(exc.context) else exc.message
            error_message = "Validation failed on {}: {}".format(
                "/".join(map(str, exc.path)), error_message.replace("@", "")
            )
            raise LabelStudioValidationErrorSentryIgnored(error_message)

    def _to_name_validation(self, config_string):
        """ """
        # toName points to existent name
        all_names = re.findall(r'name="([^"]*)"', config_string)

        names = set(all_names)
        toNames = re.findall(r'toName="([^"]*)"', config_string)
        for toName_ in toNames:
            for toName in toName_.split(","):
                if toName not in names:
                    raise LabelStudioValidationErrorSentryIgnored(
                        f'toName="{toName}" not found in names: {sorted(names)}'
                    )

    def _unique_names_validation(self, config_string):
        """ """
        # unique names in config # FIXME: 'name =' (with spaces) won't work
        all_names = re.findall(r'name="([^"]*)"', config_string)
        if len(set(all_names)) != len(all_names):
            raise LabelStudioValidationErrorSentryIgnored(
                "Label config contains non-unique names"
            )

    @property
    def is_valid(self):
        """ """
        try:
            self.validate()
            return True
        except LabelStudioValidationErrorSentryIgnored:
            return False

    def validate(self):
        """Validates the provided configuration string against various validation criteria.

        This method applies a series of validation checks to
        `_config`, including schema validation, checking for
        uniqueness of names used in the configuration, and the
        "to_name" validation. It throws exceptions if any of these
        validations fail.

        Raises:
            Exception: If any validation fails, specific to the type of validation.

        """
        config_string = self._config

        self._schema_validation(config_string)
        self._unique_names_validation(config_string)
        self._to_name_validation(config_string)

    @classmethod
    def validate_with_data(cls, config):
        """ """
        raise NotImplemented()

    def validate_task(self, task: "TaskValue", validate_regions_only=False):
        """ """
        # TODO this might not be always true, and we need to use
        # "strict" param above to be able to configure

        # for every object tag we've got that has value as it's
        # variable we need to have an associated item in the task data
        for obj in self.objects:
            if obj.value_is_variable and task["data"].get(obj.value_name, None) is None:
                return False

        if "annotations" in task and not self.validate_annotation():
            return False

        if "predictions" in task and not self.validate_prediction():
            return False

        return True

    def _validate_object(self, obj, return_errors=False) -> Union[bool, List[str]]:
        """
        Validates an object (annotation/prediction) and returns boolean or error messages.

        Args:
            obj (dict): The object to validate
            return_errors (bool): If True, returns list of error messages. If False, returns boolean.

        Returns:
            Union[bool, List[str]]: If return_errors=False, returns True/False.
                                   If return_errors=True, returns list of error messages.
        """
        errors = self._validate_object_logic(obj)
        if return_errors:
            return errors
        else:
            return len(errors) == 0

    def _validate_object_logic(self, obj) -> List[str]:
        """Core validation logic that returns error messages."""
        errors = []

        try:
            # Check if result key exists
            if RESULT_KEY not in obj:
                errors.append(f"Missing required field '{RESULT_KEY}'")
                return errors

            result = obj.get(RESULT_KEY)
            if not isinstance(result, list):
                errors.append(f"'{RESULT_KEY}' must be a list")
                return errors

            # Validate score if present
            if 'score' in obj:
                score = obj['score']
                if score is not None:
                    try:
                        score_float = float(score)
                        if not (0.0 <= score_float <= 1.0):
                            errors.append(f"Score must be between 0.00 and 1.00 inclusive, got {score_float}")
                    except (ValueError, TypeError):
                        errors.append(f"Score must be a valid number, got {score}")

            regions = []
            relations_to_validate = []

            # Validate each region
            for i, region in enumerate(result):
                if not isinstance(region, dict):
                    errors.append(f"Region must be a dictionary. Got {type(region)}: {region}")
                    continue

                if region.get('type') != "relation":
                    region_errors = self.validate_region(region, return_errors=True, region_index=i)
                    errors.extend(region_errors)
                    if not region_errors:  # Only add to regions if no errors
                        regions.append(region)
                else:
                    # Store relation for later validation
                    relations_to_validate.append((i, region))

            # Validate relations after all regions are processed
            for i, relation in relations_to_validate:
                relation_error = self.validate_relation(relation, regions, return_errors=True, relation_index=i)
                if relation_error:
                    errors.append(relation_error)

        except Exception as e:
            errors.append(f"Unexpected error during validation: {str(e)}")

        return errors


    def validate_annotation(self, annotation):
        """Validates the given annotation against the current configuration.

        This method applies the `validate_region` method to each
        region in the annotation and returns False if any of these
        validations fail. If all the regions pass the validation, it
        returns True.

        Args:
            annotation (dict): The annotation to be validated, where
            each key-value pair denotes an attribute-value of the
            annotation.

        Returns:
            bool: True if all regions in the annotation pass the
            validation, False otherwise.

        """
        return self._validate_object(annotation)

    def validate_prediction(self, prediction, return_errors=False):
        """
        Validates the given prediction against the current configuration.

        Args:
            prediction (dict): The prediction to be validated
            return_errors (bool): If True, returns a list of error messages instead of boolean

        Returns:
            Union[bool, List[str]]: If return_errors=False, returns True/False.
                                   If return_errors=True, returns list of error messages.
        """
        return self._validate_object(prediction, return_errors)

    def _validate_region_logic(self, region, region_index=0) -> Tuple[bool, List[str]]:
        """Helper method to perform region validation logic.

        Args:
            region (dict): The region to be validated.
            region_index (int): Index of the region for error reporting.

        Returns:
            tuple: (is_valid, errors) where is_valid is bool and errors is list of strings.
        """
        errors = []

        # Check required fields
        required_fields = ['from_name', 'to_name', 'type', 'value']
        for field in required_fields:
            if field not in region:
                errors.append(f"Region {region_index}: Missing required field '{field}'")

        # If missing required fields, don't continue validation
        if errors:
            return False, errors

        # Validate from_name exists in configuration
        try:
            control = self.get_control(region["from_name"])
        except Exception as e:
            errors.append(f"Region {region_index}: 'from_name' '{region['from_name']}' not found in configuration")
            return False, errors

        # Validate to_name exists in configuration
        try:
            obj = self.get_object(region["to_name"])
        except Exception as e:
            errors.append(f"Region {region_index}: 'to_name' '{region['to_name']}' not found in configuration")
            return False, errors

        # Validate type matches control tag
        expected_type = control.tag.lower()
        actual_type = region["type"].lower()
        if actual_type != expected_type:
            errors.append(f"Region {region_index}: Type '{actual_type}' does not match expected type '{expected_type}' for control '{region['from_name']}'")

        # Validate to_name is in control's to_name list
        if region["to_name"] not in control.to_name:
            errors.append(f"Region {region_index}: 'to_name' '{region['to_name']}' is not valid for control '{region['from_name']}'. Valid options: {control.to_name}")

        # Validate the value using control's validate_value method
        try:
            if not control.validate_value(region["value"]):
                # Prefer a clearer message for rectangle geometry bounds
                tag_lower = getattr(control, 'tag', '').lower()
                if tag_lower in ('rectangle', 'rectanglelabels'):
                    out_of_bounds_fields = []
                    value = region["value"]
                    for field in ("x", "y", "width", "height"):
                        if field in value:
                            try:
                                v = float(value[field])
                                if v < 0 or v > 100:
                                    out_of_bounds_fields.append(f"{field} {value[field]}")
                            except Exception:
                                out_of_bounds_fields.append(f"{field} {value[field]}")
                    if out_of_bounds_fields:
                        errors.append(
                            f"Region {region_index}: Invalid geometry for control '{region['from_name']}': "
                            + ", ".join(out_of_bounds_fields)
                            + " out of bounds [0, 100]"
                        )
                    else:
                        invalid_value = region["value"]
                        valid_values = self._get_valid_values_for_control(control)
                        errors.append(
                            f"Region {region_index}: Invalid value for control '{region['from_name']}'. Got: {invalid_value}. Valid options: {valid_values}"
                        )
                else:
                    invalid_value = region["value"]
                    valid_values = self._get_valid_values_for_control(control)
                    errors.append(
                        f"Region {region_index}: Invalid value for control '{region['from_name']}'. Got: {invalid_value}. Valid options: {valid_values}"
                    )
        except Exception as e:
            errors.append(f"Region {region_index}: Error validating value for control '{region['from_name']}': {str(e)}")

        return len(errors) == 0, errors

    def _get_valid_values_for_control(self, control):
        """Get valid values for a control tag to provide better error messages."""
        try:
            if hasattr(control, 'labels') and control.labels:
                # For tags with predefined labels (Choices, Labels, etc.)
                return f"{control.labels}"
            elif hasattr(control, '_value_class'):
                # For tags with value classes, show the expected structure
                return f"expected structure: {control._value_class.__name__}"
            else:
                return "no specific validation rules"
        except Exception:
            return "unknown validation rules"

    def validate_region(self, region, return_errors=False, region_index=0):
        """Validates a region from the annotation against the current
        configuration.

        The validation checks the following:
        - Both control and object items are present in the labeling configuration.
        - The type of the region matches the control tag name.
        - The 'to_name' in the region data connects to the same tag as in the configuration.
        - The actual value for example in <Labels /> tag is producing start, end, and labels.

        Args:
            region (dict): The region to be validated.
            return_errors (bool): If True, returns a list of error messages instead of boolean
            region_index (int): Index of the region for error reporting (used when return_errors=True)

        Returns:
            Union[bool, List[str]]: If return_errors=False, returns True/False.
                                   If return_errors=True, returns list of error messages.
        """
        is_valid, errors = self._validate_region_logic(region, region_index)

        if return_errors:
            return errors
        else:
            return is_valid

    def _validate_relation_logic(self, relation, regions, relation_index=0) -> Tuple[bool, List[str]]:
        """Helper method to perform relation validation logic.
        Args:
            relation (dict): The relation to validate
            regions (list): List of validated regions
            relation_index (int): Index of the relation for error reporting

        Returns:
            tuple: (is_valid, errors) where is_valid is bool and errors is list of strings.
        """
        errors = []

        try:
            # Check required fields for relations
            required_fields = ['type', 'direction', 'from_id', 'to_id']
            for field in required_fields:
                if field not in relation:
                    errors.append(f"Relation {relation_index}: Missing required field '{field}'")

            # Validate type
            if relation.get("type") != "relation":
                errors.append(f"Relation {relation_index}: Type must be 'relation', got '{relation.get('type')}'")

            # Validate direction
            valid_directions = ("left", "right", "bi")
            if relation.get("direction") not in valid_directions:
                errors.append(f"Relation {relation_index}: Direction must be one of {valid_directions}, got '{relation.get('direction')}'")

            # Create mapping of region IDs
            region_mapping = {r['id']: r for r in regions if 'id' in r}

            # Validate from_id exists
            from_id = relation.get("from_id")
            if from_id not in region_mapping:
                errors.append(f"Relation {relation_index}: 'from_id' '{from_id}' not found in regions")

            # Validate to_id exists
            to_id = relation.get("to_id")
            if to_id not in region_mapping:
                errors.append(f"Relation {relation_index}: 'to_id' '{to_id}' not found in regions")

        except Exception as e:
            errors.append(f"Relation {relation_index}: Error validating relation - {str(e)}")

        return len(errors) == 0, errors

    def validate_relation(self, relation, regions, return_errors=False, relation_index=0):
        """Validates that the relation is correct and all the associated objects are provided

        Args:
            relation (dict): The relation to validate
            regions (list): List of validated regions
            return_errors (bool): If True, returns error message string instead of boolean
            relation_index (int): Index of the relation for error reporting (used when return_errors=True)

        Returns:
            Union[bool, str]: If return_errors=False, returns True/False.
                             If return_errors=True, returns error message string or None.
        """
        is_valid, errors = self._validate_relation_logic(relation, regions, relation_index)

        if return_errors:
            return errors
        else:
            return is_valid

    ### Generation

    def _sample_task(self, secure_mode=False):
        """ """
        # predefined_task, annotations, predictions = get_task_from_labeling_config(label_config)
        generated_task = self.generate_sample_task(
            mode="editor_preview", secure_mode=secure_mode
        )

        if self._sample_config_task is not None:
            generated_task.update(self._sample_config_task)

        return generated_task, self._sample_config_ann, self._sample_config_pred

    def generate_sample_task(self, mode="upload", secure_mode=False):
        """Generates a sample task based on the provided mode and
        secure_mode.

        This function generates an example value for each object in
        `self.objects` using the specified `mode` and
        `secure_mode`. The resulting task is a dictionary where each
        key-value pair denotes an object's value-name and example
        value.

        Args:
            mode (str, optional): The operation mode. Accepts any string but defaults to 'upload'.
            secure_mode (bool, optional): The security mode. Defaults to False.

        Returns:
            dict: A dictionary representing the sample task.

        """
        task = {
            obj.value_name: obj.generate_example_value(
                mode=mode, secure_mode=secure_mode
            )
            for obj in self.objects
        }

        return task

    def _generate_sample_regions(self):
        """ Generate an example of each control tag's JSON schema and validate it as a region"""
        return self.create_regions({
            control.name: JSF(control.to_json_schema()).generate()
            for control in self.controls
        })

    def generate_sample_prediction(self) -> Optional[dict]:
        """Generates a sample prediction that is valid for this label config.

        Example:
            {'model_version': 'sample model version',
             'score': 0.0,
             'result': [{'id': 'e7bd76e6-4e88-4eb3-b433-55e03661bf5d',
               'from_name': 'sentiment',
               'to_name': 'text',
               'type': 'choices',
               'value': {'choices': ['Neutral']}}]}

        NOTE: `id` field in result is not required when importing predictions; it will be generated automatically.
        NOTE: for each control tag, depends on tag.to_json_schema() being implemented correctly
        """
        prediction = PredictionValue(
            model_version='sample model version',
            result=self._generate_sample_regions()
        )
        prediction_dct = prediction.model_dump()
        if self.validate_prediction(prediction_dct):
            return prediction_dct
        else:
            logger.debug(f'Sample prediction {prediction_dct} failed validation for label config {self.config}')
            return None

    def generate_sample_annotation(self) -> Optional[dict]:
        """Generates a sample annotation that is valid for this label config.

        Example:
            {'was_cancelled': False,
             'ground_truth': False,
             'lead_time': 0.0,
             'result_count': 0,
             'completed_by': -1,
             'result': [{'id': 'b05da11d-3ffc-4657-8b8d-f5bc37cd59ac',
               'from_name': 'sentiment',
               'to_name': 'text',
               'type': 'choices',
               'value': {'choices': ['Negative']}}]}

        NOTE: `id` field in result is not required when importing predictions; it will be generated automatically.
        NOTE: for each control tag, depends on tag.to_json_schema() being implemented correctly
        """
        annotation = AnnotationValue(
            completed_by=-1,  # annotator's user id
            result=self._generate_sample_regions()
        )
        annotation_dct = annotation.model_dump()
        if self.validate_annotation(annotation_dct):
            return annotation_dct
        else:
            logger.debug(f'Sample annotation {annotation_dct} failed validation for label config {self.config}')
            return None

    def generate_complete_sample_task(self, raise_on_failure: bool = False) -> Optional[dict]:
        """Generate a complete sample task with annotations and predictions.

        This method combines the generation of a sample task, sample prediction, and sample annotation
        into a single method call, returning a complete task structure.

        Args:
            raise_on_failure: If True, will raise ValueError when any step
                              (including annotation/prediction generation) fails

        Raises:
            ValueError: If raise_on_failure is True and any generation step fails.

        Example:
            {
              'data': {'text': 'Sample text for labeling'},
              'annotations': [
                {'was_cancelled': False,
                 'ground_truth': False,
                 'completed_by': -1,
                 'result': [
                   {'id': 'b05da11d-3ffc-4657-8b8d-f5bc37cd59ac',
                    'from_name': 'sentiment',
                    'to_name': 'text',
                    'type': 'choices',
                    'value': {'choices': ['Negative']}}
                 ]
                }
              ],
              'predictions': [
                {'model_version': 'sample model version',
                 'score': 0.95,
                 'result': [
                   {'id': 'e7bd76e6-4e88-4eb3-b433-55e03661bf5d',
                    'from_name': 'sentiment',
                    'to_name': 'text',
                    'type': 'choices',
                    'value': {'choices': ['Neutral']}}
                 ]
                }
              ]
            }

        NOTE: `id` field in result is not required when importing predictions; it will be generated automatically.
        NOTE: for each control tag, depends on tag.to_json_schema() being implemented correctly
        """
        sample_task = self.generate_sample_task()
        if not sample_task:
            if raise_on_failure:
                raise ValueError("LabelInterface.generate_sample_task failed to generate a valid sample task")
            return None

        sample_prediction = self.generate_sample_prediction()
        if not sample_prediction and raise_on_failure:
            raise ValueError("LabelInterface.generate_sample_prediction failed to generate a valid prediction")

        sample_annotation = self.generate_sample_annotation()
        if not sample_annotation and raise_on_failure:
            raise ValueError("LabelInterface.generate_sample_annotation failed to generate a valid annotation")

        return {
            "data": sample_task,
            "annotations": [sample_annotation] if sample_annotation else [],
            "predictions": [sample_prediction] if sample_prediction else []
        }

    #####
    ##### COMPATIBILITY LAYER
    #####
    ##### This are re-implmenetation of functions found in different
    ##### label_config.py files across the repo. Not all of this were
    ##### tested, therefore I suggest to write a test first, and then
    ##### replace where it's being used in the repo.

    def config_essential_data_has_changed(self, new_config_str):
        """Detect essential changes of the labeling config"""
        new_obj = LabelInterface(config=new_config_str)

        for new_tag_name, new_tag in new_obj._controls.items():
            if new_tag_name not in self._controls:
                return True

            old_tag = self._controls[new_tag_name]

            if new_tag.tag != old_tag.tag:
                return True
            if new_tag.objects != old_tag.objects:
                return True
            if not set(old_tag.labels).issubset(new_tag.labels):
                return True

        return False

    def generate_sample_task_without_check(
        label_config, mode="upload", secure_mode=False
    ):
        """ """
        raise NotImplemented()

    @classmethod
    def get_task_from_labeling_config(cls, config):
        """Get task, annotations and predictions from labeling config comment,
        it must start from "<!-- {" and end as "} -->"
        """
        # try to get task data, annotations & predictions from config comment
        task_data, annotations, predictions = {}, None, None
        start = config.find("<!-- {")
        start = start if start >= 0 else config.find("<!--{")
        start += 4
        end = config[start:].find("-->") if start >= 0 else -1

        if 3 < start < start + end:
            try:
                # logger.debug('Parse ' + config[start : start + end])
                body = json.loads(config[start : start + end])
            except Exception:
                # logger.error("Can't parse task from labeling config", exc_info=True)
                pass
            else:
                # logger.debug(json.dumps(body, indent=2))
                dont_use_root = "predictions" in body or "annotations" in body
                task_data = (
                    body["data"]
                    if "data" in body
                    else (None if dont_use_root else body)
                )
                predictions = body["predictions"] if "predictions" in body else None
                annotations = body["annotations"] if "annotations" in body else None

        return task_data, annotations, predictions

    @classmethod
    def config_line_stipped(self, c):
        tree = etree.fromstring(c, forbid_dtd=False)
        comments = tree.xpath("//comment()")

        for c in comments:
            p = c.getparent()
            if p is not None:
                p.remove(c)
            c = etree.tostring(tree, method="html").decode("utf-8")

        return c.replace("\n", "").replace("\r", "")

    def get_all_control_tag_tuples(label_config):
        """ """
        return [tag.as_tuple() for tag in self.controls]

    def get_first_tag_occurence(
        self,
        control_type: Union[str, Tuple],
        object_type: Union[str, Tuple],
        name_filter: Optional[Callable] = None,
        to_name_filter: Optional[Callable] = None,
    ) -> Tuple[str, str, str]:
        """
        Reads config and fetches the first control tag along with first object tag that matches the type.

        Args:
          control_type (str or tuple): The control type for checking tag matches.
          object_type (str or tuple): The object type for checking tag matches.
          name_filter (function, optional): If given, only tags with this name will be considered.
                                           Default is None.
          to_name_filter (function, optional): If given, only tags with this name will be considered.
                                              Default is None.

        Returns:
          tuple: (from_name, to_name, value), representing control tag, object tag and input value.
        """

        for tag in self.controls:
            if tag.match(control_type, name_filter_fn=name_filter):
                for object_tag in tag.objects:
                    if object_tag.match(object_type, to_name_filter_fn=to_name_filter):
                        return tag.name, object_tag.name, object_tag.value_name

        raise ValueError(
            f"No control tag of type {control_type} and object tag of type {object_type} found in label config"
        )

    def get_all_labels(self):
        """ """
        dynamic_values = {c.name: True for c in self.controls if c.dynamic_value}
        return self._labels, dynamic_values

    def get_all_object_tag_names(self):
        """ """
        return self._objects.keys()

    def extract_data_types(self):
        """ """
        return self._objects

    def is_video_object_tracking(self):
        """ """
        match_fn = lambda tag: tag.tag.lower() in _VIDEO_TRACKING_TAGS
        tags = self.find_tags(match_fn=match_fn)

        return bool(tags)

    def is_type(self, tag_type=None):
        """ """
        raise NotImplemented

    # NOTE: you can use validate() instead
    # def validate_label_config(self, config_string):
    #     # xml and schema
    #     self._schema_validation(config_string)
    #     self._unique_names_validation(config_string)
    #     self._to_name_validation(config_string)

    def validate_config_using_summary(self, summary, strict=False):
        """Validate current config using LS Project Summary"""
        # this is a rewrite of project.validate_config function
        # self.validate_label_config(config_string)
        if not self._objects:
            return False

        created_labels = summary.created_labels
        created_labels_drafts = summary.created_labels_drafts
        annotations_summary = summary.created_annotations

        self.validate_annotations_consistency(annotations_summary)
        self.validate_lables_consistency(created_labels, created_labels_drafts)

    def validate_lables_consistency(self, created_labels, created_labels_drafts):
        """ """
        # validate labels consistency
        # labels_from_config, dynamic_values_tags = self.get_all_labels(config_string)

        created_labels = merge_labels_counters(created_labels, created_labels_drafts)

        # <Labels name="sentinement" ...><Label value="Negative" ... />
        # {'sentiment': {'Negative': 1, 'Positive': 3, 'Neutral': 1}}

        for control_tag_from_data, labels_from_data in created_labels.items():
            # Check if labels created in annotations, and their control tag has been removed
            control_from_config = self.get_control(control_tag_from_data)

            if labels_from_data and not control_from_config:
                raise LabelStudioValidationErrorSentryIgnored(
                    f"There are {sum(labels_from_data.values(), 0)} annotation(s) created with tag "
                    f'"{control_tag_from_data}", you can\'t remove it'
                )

            removed_labels = []
            # Check that labels themselves were not removed
            for label_name, label_value in labels_from_data.items():
                if label_value > 0 and not control_from_config.labels_attrs.get(
                    label_name, None
                ):
                    # that label was used in labeling before, but not
                    # present in the current config
                    removed_labels.append(label_name)

            # TODO that needs to be added back
            # if 'VideoRectangle' in tag_types:
            #     for key in labels_from_config:
            #         labels_from_config_by_tag |= set(labels_from_config[key])

            # if 'Taxonomy' in tag_types:
            #     custom_tags = Label.objects.filter(links__project=self).values_list('value', flat=True)
            #     flat_custom_tags = set([item for sublist in custom_tags for item in sublist])
            #     labels_from_config_by_tag |= flat_custom_tags

            if len(removed_labels):
                raise LabelStudioValidationErrorSentryIgnored(
                    f'These labels still exist in annotations or drafts:\n{",".join(removed_labels)}'
                    f'Please add labels to tag with name="{str(control_tag_from_data)}".'
                )

    def validate_annotations_consistency(self, annotations_summary):
        """ """
        # annotations_summary is coming from LS Project Summary, it's
        # format is: { "chc|text|choices": 10 }
        # which means that there are two tags, Choices, and one of
        # object tags and there are 10 annotations

        err = []
        annotations_from_data = set(annotations_summary)

        for ann in annotations_from_data:
            from_name, to_name, tag_type = ann.split("|")

            # avoid textarea to_name check (see DEV-1598)
            if tag_type.lower() == "textarea":
                continue

            try:
                control = self.get_control(from_name)
                if not control or not control.get_object(to_name):
                    err.append(
                        f"with from_name={from_name}, to_name={to_name}, type={tag_type}"
                    )
            except Exception as ex:
                err.append(
                    f"Error occurred while processing from_name={from_name}, to_name={to_name}, type={tag_type}, error: {str(ex)}"
                )

            # control = self.get_control(from_name)
            # if not control or not control.get_object(to_name):
            #     err.append(f'with from_name={from_name}, to_name={to_name}, type={tag_type}')

        if err:
            diff_str = "\n".join(err)
            raise LabelStudioValidationErrorSentryIgnored(
                f"Created annotations are incompatible with provided labeling schema, we found:\n{diff_str}"
            )
