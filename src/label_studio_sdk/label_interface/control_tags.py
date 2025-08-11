"""
"""

import xml.etree.ElementTree
from typing import Type, Dict, Optional, List, Tuple, Any, Union
from pydantic import BaseModel, confloat, Field, validator

from .base import LabelStudioTag, get_tag_class
from .region import Region
from .object_tags import ObjectTag


_NOT_CONTROL_TAGS = {
    "Filter",
}

_TAG_TO_CLASS = {
    "choices": "ChoicesTag",
    "labels": "LabelsTag",
    "brush": "BrushTag",
    "brushlabels": "BrushLabelsTag",
    "ellipse": "EllipseTag",
    "ellipselabels": "EllipseLabelsTag",
    "keypoint": "KeyPointTag",
    "keypointlabels": "KeyPointLabelsTag",
    "polygon": "PolygonTag",
    "polygonlabels": "PolygonLabelsTag",
    "rectangle": "RectangleTag",
    "rectanglelabels": "RectangleLabelsTag",
    "videorectangle": "VideoRectangleTag",
    "number": "NumberTag",
    "datetime": "DateTimeTag",
    "hypertext": "HyperTextLabelsTag",
    "pairwise": "PairwiseTag",
    "paragraphlabels": "ParagraphLabelsTag",
    "ranker": "RankerTag",
    "rating": "RatingTag",
    "relations": "RelationsTag",
    "taxonomy": "TaxonomyTag",
    "textarea": "TextAreaTag",
    "timeserieslabels": "TimeSeriesLabelsTag",
}


class ControlTag(LabelStudioTag):
    """
    Class that represents a ControlTag in Label Studio

    Attributes:
    -----------
    name : Optional[str]
        The name of the tag
    to_name : Optional[List[str]]
        The name of the object the tag maps to
    conditionals : Optional[Dict[str, Any]]
        Conditional attributes
    dynamic_value : Optional[bool]
        A flag to indicate if the value is dynamic
    objects : Optional[Any]
        The object tag that the control tag maps to
    labels : Optional[Any]
        The labels for the control tag
    labels_attrs : Optional[Any]
        The labels attributes for the control tag
    """

    name: Optional[str] = None
    to_name: Optional[List[str]] = None
    conditionals: Optional[Dict[str, Any]] = None
    dynamic_value: Optional[bool] = False
    objects: Optional[Any] = None
    labels: Optional[Any] = None
    labels_attrs: Optional[Any] = None

    @classmethod
    def validate_node(cls, tag: xml.etree.ElementTree.Element) -> bool:
        """
        Naive check if tag is a control tag

        Parameters:
        -----------
        tag : xml.etree.ElementTree.Element
            The tag to validate

        Returns:
        --------
        bool
            True if tag is a control tag, False otherwise
        """
        return bool(
            tag.attrib.get("name")
            and tag.attrib.get("toName")
            and tag.tag not in _NOT_CONTROL_TAGS
        )
        
    @property
    def is_output_required(self):
        # TextArea can be blank unless user specifies "required"="true" in the attribute
        required_in_attr = str(self.attr.get("required", "false")).lower() == "true"
        return required_in_attr or False

    def to_json_schema(self):
        """
        Converts the current ControlTag instance into a JSON Schema.

        Returns:
            dict: A dictionary representing the JSON Schema.
        """
        return {"type": "string"}

    @classmethod
    def parse_node(cls, tag: xml.etree.ElementTree.Element, tags_mapping=None) -> "ControlTag":
        """
        Parse tag into a tag info

        Parameters:
        -----------
        tag : xml.etree.ElementTree.Element
            The tag to parse

        Returns:
        --------
        ControlTag
            The parsed tag
        """
        tag_class = get_tag_class(tag.tag, _TAG_TO_CLASS, re_mapping=tags_mapping) or cls
        if isinstance(tag_class, str):
            tag_class = globals().get(tag_class, None)
        
        tag_info = {
            "tag": tag.tag,
            "name": tag.attrib["name"],
            "to_name": tag.attrib["toName"].split(","),
            "attr": dict(tag.attrib),
        }

        # Grab conditionals if any
        conditionals = {}
        if tag.attrib.get("perRegion") == "true":
            if tag.attrib.get("whenTagName"):
                conditionals = {"type": "tag", "name": tag.attrib["whenTagName"]}
            elif tag.attrib.get("whenLabelValue"):
                conditionals = {
                    "type": "label",
                    "name": tag.attrib["whenLabelValue"],
                }
            elif tag.attrib.get("whenChoiceValue"):
                conditionals = {
                    "type": "choice",
                    "name": tag.attrib["whenChoiceValue"],
                }

        if conditionals:
            tag_info["conditionals"] = conditionals

        val = tag.attrib.get("value", None)
        if (val is not None and len(val) and val[0] == "$") or \
           tag.attrib.get("apiUrl"):
            tag_info["dynamic_value"] = True

        return tag_class(**tag_info)

    def collect_attrs(self):
        """Return tag attrs as a single dict"""
        return {
            **self.attr,
            "name": self.name,
            "toName": self.to_name
        }
    
    def get_object(self, name=None):
        """
        This method retrieves the object tag that the control tag maps to.

        Parameters:
        -----------
        name : Optional[str]
            The name of the object tag to retrieve. If not provided, the method will return the first object tag.

        Returns:
        --------
        Any
            The object tag that the control tag maps to.
        """
        return self.get_input(name=name)

    def get_input(self, name=None):
        """
        This method retrieves the object tag that the control tag maps to based on the provided name.

        Parameters:
        -----------
        name : Optional[str]
            The name of the object tag to retrieve. If not provided, the method will return the first object tag if there is only one.
            If there are multiple object tags and no name is provided, an exception will be raised.

        Returns:
        --------
        Any
            The object tag that the control tag maps to.

        Raises:
        -------
        Exception
            If the provided name is not found in the object tags or if there are multiple object tags and no name is provided.
        """
        if name is not None:
            if name not in self.to_name:
                raise Exception(f"Object name {name} is not found")

            for tag in self.objects:
                if tag.name == name:
                    return tag

        if len(self.objects) > 1:
            raise Exception("Multiple object tags connected, you should specify name")

        return self.objects[0]

    def set_labels_attrs(self, labels_attrs):
        """
        This method sets the labels attributes for the ControlTag.

        Parameters:
        -----------
        labels_attrs : Any
            The labels attributes to set for the ControlTag.
        """
        self.labels_attrs = labels_attrs

    def set_object(self, tag: ObjectTag):
        """
        This method sets the object tag that the control tag maps to.

        Parameters:
        -----------
        tag : ObjectTag
            The object tag to set for the control tag.
        """
        self.set_objects([tag])

    def set_objects(self, objects: List[ObjectTag]):
        """
        This method sets the object tags that the control tag maps to.

        Parameters:
        -----------
        objects : List[ObjectTag]
            The object tags to set for the control tag.
        """
        self.objects = objects

    def set_labels(self, labels: List[str]):
        """
        Set labels for the ControlTag
        """
        self.labels = labels

    def find_object_by_name(self, name: str) -> Optional[ObjectTag]:
        """
        This method finds and returns an object tag with the specified name from the list of object tags.

        Parameters:
        -----------
        name : str
            The name of the object tag to find.

        Returns:
        --------
        Optional[ObjectTag]
            The object tag with the specified name if found, None otherwise.
        """
        for obj in self.objects:
            if obj.name == name:
                return obj

    def _validate_labels(self, labels):
        """Check that labels is a subset of self.labels, used for
        example when you're validate the annotation or prediction to
        make sure there no undefined labels used.

        """
        if not self.labels or not labels:
            return True

        return set(labels).issubset(set(self.labels))

    def _validate_value_labels(self, value):
        """ """
        if hasattr(self, "_label_attr_name") and self._label_attr_name in value:
            return self._validate_labels(value.get(self._label_attr_name))
        return False

    def validate_value(self, value: dict) -> bool:
        """
        Given "value" from [annotation result format](https://labelstud.io/guide/task_format),
        validate if it's a valid value for this control tag.

        Parameters:
        -----------
        value : dict
            The value to validate
            Example:
            ```python
            RectangleTag(name="rect", to_name=["img"], tag="rectangle", attr={}).validate_value({"x": 10, "y": 10, "width": 10, "height": 10, "rotation": 10})
            ```

        Returns:
        --------
        bool
            True if the value is valid, False otherwise
        """
        
        # Accept inputs that nest the payload under the control name, e.g. {"ranker": "rank": ["a", "b", "c"]}
        if isinstance(value, dict) and self.name in value and isinstance(value[self.name], dict):
            value = value[self.name]

        if hasattr(self, "_label_attr_name"):
            if not self._validate_value_labels(value):
                return False

        try:
            inst = self._value_class(**value)
            return True
        except Exception as e:
            return False

    def _resolve_to_name(self, to_name: Optional[str] = None) -> str:
        """
        This method resolves the name of the object tag that the control tag maps to.
        If a name is provided and it is found in the control tag, it is returned.
        If no name is provided and there is only one object tag, its name is returned.
        If no name is provided and there are multiple object tags, an exception is raised.

        Parameters:
        -----------
        to_name : Optional[str]
            The name of the object tag to resolve. If not provided, the method will return the name of the first object tag if there is only one.

        Returns:
        --------
        str
            The name of the object tag that the control tag maps to.

        Raises:
        -------
        Exception
            If the provided name is not found in the object tags or if there are multiple object tags and no name is provided.
        """
        if to_name:
            if to_name not in self.to_name:
                raise Exception("To name is not found in control tag")

            return to_name
        else:
            # TODO: "Pairwise" tag has multiple to_name
            # if len(self.to_name) > 1:
            #     raise Exception(
            #         "Multiple to_name in control tag, specify to_name in function"
            #     )

            return self.to_name[0]

    def _label_simple(self, to_name: Optional[str] = None, *args, **kwargs) -> Region:
        """
        This method creates a new Region object with the specified label applied.
        It first resolves the name of the object tag that the control tag maps to.
        Then it finds the object tag with the resolved name.
        It creates a new instance of the value class with the provided arguments and keyword arguments.
        Finally, it returns a new Region object with the current control tag, the found object tag, and the created value.

        Parameters:
        -----------
        to_name : Optional[str]
            The name of the object tag to resolve. If not provided, the method will return the name of the first object tag if there is only one.
        *args : tuple
            Variable length argument list.
        **kwargs : dict
            Arbitrary keyword arguments.

        Returns:
        --------
        Region
            A new Region object with the specified label applied.
        """
        to_name = self._resolve_to_name(to_name)
        obj = self.find_object_by_name(to_name)
        cls = self._value_class
        value = cls(**kwargs)
        
        return Region(from_tag=self, to_tag=obj, value=value)

    def _label_with_labels(
        self,
        label: Union[str, List[str]] = None,
        to_name: Optional[str] = None,
        *args,
        **kwargs,
    ) -> Region:
        """
        This method creates a new Region object with the specified label applied.
        It first checks if the label is a string and if so, converts it to a list.
        Then it validates the labels and raises an exception if they are not valid.
        It adds the labels to the keyword arguments under the attribute name for labels.
        Finally, it calls the _label_simple method to create and return a new Region object.

        Parameters:
        -----------
        label : Union[str, List[str]], optional
            The label to be applied. If a string is provided, it is converted to a list.
        to_name : Optional[str], optional
            The name of the object tag to resolve. If not provided, the method will return the name of the first object tag if there is only one.
        *args : tuple
            Variable length argument list.
        **kwargs : dict
            Arbitrary keyword arguments.

        Returns:
        --------
        Region
            A new Region object with the specified label applied.

        Raises:
        -------
        Exception
            If the labels are not valid.
        """
        if isinstance(label, str):
            label = [label]

        if not self._validate_labels(label):
            raise ValueError(
                f"Using labels not defined in labeling config, possible values: {set(self.labels)}"
            )

        kwargs[self._label_attr_name] = label
        
        return self._label_simple(to_name=to_name, **kwargs)

    def label(
        self,
        label: Optional[Union[str, List[str]]] = None,
        to_name: Optional[str] = None,
        *args,
        **kwargs,
    ) -> Region:
        """
        This method creates a new Region object with the specified label.
        
        If labels are provided, it creates a new instance of the value class with the provided arguments and keyword arguments and adds the labels to the Region object.

        Parameters:
        -----------
        label : Optional[Union[str, List[str]]]
            The label to be applied. If a string is provided, it is converted to a list.
        to_name : Optional[str]
            The name of the object tag to resolve. If not provided, the method will return the name of the first object tag if there is only one.
        *args : tuple
            Variable length argument list.
        **kwargs : dict
            Arbitrary keyword arguments.

        Returns:
        --------
        Region
            A new Region object with the specified label applied.
        """
        if hasattr(self, "_label_attr_name") and label is not None:
            return self._label_with_labels(
                label=label, to_name=to_name, *args, **kwargs
            )
        else:
            return self._label_simple(to_name=to_name, *args, **kwargs)
        
    def get_labels(self, regions: List[Dict]):
        """
        Returns the simplified representation of the label. Sort of a reverse to label() method to retrieve an input `label` from an output regions
        """
        values = [region.get('value') for region in regions if region.get('from_name') == self.name]
        values = list(filter(lambda x: x is not None, values))
        if not hasattr(self, "_label_attr_name"):
            return values
        labels = []
        for value in values:
            if len(value) == 1 and self._label_attr_name in value:
                v = value[self._label_attr_name]
                labels.append(v[0] if type(v) == list and len(v) == 1 else v)
            else:
                labels.append(value)
        return labels[0] if len(labels) == 1 else labels

    def as_tuple(self):
        """ """
        from_name = self.name
        to_name = self.to_name
        tag_type = self.tag

        if isinstance(to_name, list):
            to_name = ",".join(to_name)

        return "|".join([from_name, to_name, type.lower()])


class SpanSelection(BaseModel):
    start: Union[int, str]
    end: Union[int, str]


class SpanSelectionOffsets(SpanSelection):
    startOffset: Optional[int] = Field(None, ge=0)
    endOffset: Optional[int] = Field(None, ge=0)


class ChoicesValue(BaseModel):
    choices: List[str]


class ChoicesTag(ControlTag):
    """ """
    tag: str = "Choices"
    _label_attr_name: str = "choices"
    _value_class: Type[ChoicesValue] = ChoicesValue

    @property
    def is_multiple_choice(self):
        return self.attr.get("choice") == "multiple"

    def to_json_schema(self):
        """
        Converts the current ChoicesTag instance into a JSON Schema.

        Returns:
            dict: A dictionary representing the JSON Schema compatible with OpenAPI 3.
        """
        if self.is_multiple_choice:
            return {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": self.labels,
                },
                "uniqueItems": True,
                "description": f"Choices for {self.to_name[0]}",
            }

        return {
            "type": "string",
            "enum": self.labels,
            "description": f"Choices for {self.to_name[0]}"
        }


class LabelsValue(SpanSelection):
    labels: List[str]


class LabelsTag(ControlTag):
    """ """
    tag: str = "Labels"
    _label_attr_name: str = "labels"
    _value_class: Type[LabelsValue] = LabelsValue

    def to_json_schema(self):
        """
        Converts the current LabelsTag instance into a JSON Schema.

        Returns:
            dict: A dictionary representing the JSON Schema compatible with OpenAPI 3.
        """
        return {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["start", "end", "labels"],
                "properties": {
                    "start": {
                        "type": "integer",
                        # TODO: this is incompatible with the OpenAI API using PredictedOutputs
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
                            "enum": self.labels
                        }
                    },
                    "text": {
                        "type": "string"
                    }
                }
            },
            "description": f"Labels and span indices for {self.to_name[0]}"
        }

## Image tags

def validate_rle(list):
    """
    Validate if a list is correctly formatted in Run-Length Encoding (RLE).

    A correctly formatted RLE list should follow 'value, count' pairs. 
    For example, [2,3,3,2] is a valid RLE list representing [2,2,2,3,3].

    Parameters:
        list : a list of integers

    Returns:
        bool : True if the list is correctly formatted in RLE, False otherwise
    """
    # If the list length is odd, it's invalid.
    if len(list) % 2 != 0:
        return False

    # Check 'value, count' pairs. The count should always be greater than zero.
    for i in range(1, len(list), 2):
        if list[i] <= 0:
            return False

    return True


class BrushValue(BaseModel):
    format: str = "rle"
    rle: List[int]

    @validator('rle')
    def validate_rle(cls, rle_data):
        if not validate_rle(rle_data):
            raise ValueError('Invalid RLE format')
        
        return rle_data


class BrushLabelsValue(BrushValue):
    brushlabels: List[str]


class BrushTag(ControlTag):
    """ """
    tag: str = "Brush"
    _value_class: Type[BrushValue] = BrushValue

    # def validate_value(self, value) -> bool:
    #     res = super().validate_value(value)
    #     if res is True and value.get("format") == "rle":
    #         return validate_rle(value.get("rle"))
        
    #     return res

class BrushLabelsTag(BrushTag):
    """ """
    tag: str = "BrushLabels"
    _label_attr_name: str = "brushlabels"
    _value_class: Type[BrushLabelsValue] = BrushLabelsValue


class EllipseValue(BaseModel):
    x: confloat(le=100)
    y: confloat(le=100)
    radiusX: confloat(le=50)
    radiusY: confloat(le=50)
    rotation: Optional[confloat(le=360)] = 0


class EllipseLabelsValue(EllipseValue):
    ellipselabels: List[str]


class EllipseTag(ControlTag):
    """ """
    tag: str = "Ellipse"
    _value_class: Type[EllipseValue] = EllipseValue


class EllipseLabelsTag(ControlTag):
    """ """
    tag: str = "EllipseLabels"
    _label_attr_name: str = "ellipselabels"
    _value_class: Type[EllipseLabelsValue] = EllipseLabelsValue


class KeyPointValue(BaseModel):
    x: confloat(le=100)
    y: confloat(le=100)


class KeyPointLabelsValue(KeyPointValue):
    keypointlabels: List[str]


class KeyPointTag(ControlTag):
    """ """
    tag: str = "KeyPoint"
    _value_class: Type[KeyPointValue] = KeyPointValue


class KeyPointLabelsTag(ControlTag):
    """ """
    tag: str = "KeyPointLabels"
    _label_attr_name: str = "keypointlabels"
    _value_class: Type[KeyPointLabelsValue] = KeyPointLabelsValue


class PolygonValue(BaseModel):
    points: List[Tuple[confloat(le=100), confloat(le=100)]]


class PolygonLabelsValue(PolygonValue):
    polygonlabels: List[str]


class PolygonTag(ControlTag):
    """ """
    tag: str = "Polygon"
    _value_class: Type[PolygonValue] = PolygonValue


class PolygonLabelsTag(ControlTag):
    """ """
    tag: str = "PolygonLabels"
    _label_attr_name: str = "polygonlabels"
    _value_class: Type[PolygonLabelsValue] = PolygonLabelsValue


class RectangleValue(BaseModel):
    x: confloat(le=100)
    y: confloat(le=100)
    width: confloat(le=100)
    height: confloat(le=100)
    rotation: Optional[confloat(le=360)] = 0


class RectangleLabelsValue(RectangleValue):
    rectanglelabels: List[str]


class RectangleTag(ControlTag):
    """ """
    tag: str = "Rectangle"
    _value_class: Type[RectangleValue] = RectangleValue


class RectangleLabelsTag(ControlTag):
    """ """
    tag: str = "RectangleLabels"
    _label_attr_name: str = "rectanglelabels"
    _value_class: Type[RectangleLabelsValue] = RectangleLabelsValue


class VideoRectangleSequenceValue(BaseModel):
    x: confloat(le=100)
    y: confloat(le=100)
    time: float
    frame: int
    width: confloat(le=100)
    height: confloat(le=100)
    rotation: Optional[float] = 0


class VideoRectangleValue(BaseModel):
    framesCount: int
    duration: float
    sequence: List[VideoRectangleSequenceValue]
    labels: Optional[List[str]]
    
    
class VideoRectangleTag(ControlTag):
    """ """
    tag: str = "VideoRectangle"
    _label_attr_name: str = "labels"
    _value_class: Type[VideoRectangleValue] = VideoRectangleValue
    
    
class NumberValue(BaseModel):
    number: int = Field(..., ge=0)
    

class NumberTag(ControlTag):
    """ """
    tag: str = "Number"
    _value_class: Type[NumberValue] = NumberValue
    _label_attr_name: str = "number"

    def to_json_schema(self):
        """
        Converts the current NumberTag instance into a JSON Schema.

        Returns:
            dict: A dictionary representing the JSON Schema compatible with OpenAPI 3.
        """
        schema = {
            "type": "number",
            "description": f"Number for {self.to_name[0]}"
        }
        
        if 'min' in self.attr:
            schema["minimum"] = float(self.attr['min'])
        if 'max' in self.attr:
            schema["maximum"] = float(self.attr['max'])
        
        return schema
    

class DateTimeValue(BaseModel):
    datetime: str

    
class DateTimeTag(ControlTag):
    """ """
    tag: str = "DateTime"
    _value_class: Type[DateTimeValue] = DateTimeValue
    _label_attr_name: str = "datetime"

    def _label_simple(self, to_name: Optional[str] = None, *args, **kwargs) -> Region:
        # TODO: temporary fix to force datetime to be a string
        kwargs['datetime'] = kwargs['datetime'][0]
        return super()._label_simple(to_name, *args, **kwargs)

    def to_json_schema(self):
        """
        Converts the current DateTimeTag instance into a JSON Schema.

        Returns:
            dict: A dictionary representing the JSON Schema compatible with OpenAPI 3.
        """
        return {
            "type": "string",
            "format": "date-time",
            "description": f"Date and time for {self.to_name[0]}"
        }


class HyperTextLabelsValue(SpanSelectionOffsets):
    htmllabels: List[str]


class HyperTextLabelsTag(ControlTag):
    """ """
    tag: str = "HyperTextLabels"
    _label_attr_name: str = "htmllabels"
    _value_class: Type[HyperTextLabelsValue] = HyperTextLabelsValue


class PairwiseValue(BaseModel):
    selected: str


class PairwiseTag(ControlTag):
    """ """
    tag: str = "Pairwise"
    _value_class: Type[PairwiseValue] = PairwiseValue
    _label_attr_name: str = "selected"

    def label(self, label):
        """ """
        value = PairwiseValue(selected=label)
        # <Pairwise> tag has equal from_name and to_name, and string label that's not a list of strings
        return Region(from_tag=self, to_tag=self, value=value)

    def to_json_schema(self):
        """
        Converts the current PairwiseTag instance into a JSON Schema.

        Returns:
            dict: A dictionary representing the JSON Schema compatible with OpenAPI 3.
        """
        return {
            "type": "string",
            "enum": ["left", "right"],
            "description": f"Pairwise selection between {self.to_name[0]} (left) and {self.to_name[1]} (right)"
        }


class ParagraphLabelsValue(SpanSelectionOffsets):
    paragraphlabels: List[str]


class ParagraphLabelsTag(ControlTag):
    """ """
    tag: str = "ParagraphsLabels"
    _label_attr_name: str = "paragraphlabels"
    _value_class: Type[ParagraphLabelsValue] = ParagraphLabelsValue

    def label(self, utterance=None, *args, **kwargs):
        """ """
        if isinstance(utterance, int):
            kwargs["start"] = utterance
            kwargs["end"] = utterance

        return super().label(*args, **kwargs)
        

class RankerValue(BaseModel):
    rank: List[str]

    
class RankerTag(ControlTag):
    """ """
    tag: str = "Ranker"
    _value_class: Type[RankerValue] = RankerValue


class RatingValue(BaseModel):
    rating: int = Field(..., ge=0)


class RatingTag(ControlTag):
    """ """
    tag: str = "Rating"
    _value_class: Type[RatingValue] = RatingValue
    _label_attr_name: str = "rating"

    def _validate_value_labels(self, value):
        """Override to handle rating values correctly - ratings are not labels"""
        if self._label_attr_name not in value:
            return False

        # For ratings, we just check that the rating value exists and is valid
        # The actual validation is done by the RatingValue model
        rating_value = value.get(self._label_attr_name)
        if rating_value is None:
            return False

        # Check if rating is within valid range (0 to maxRating)
        max_rating = int(self.attr.get('maxRating', 5))
        try:
            rating_int = int(rating_value)
            return 0 <= rating_int <= max_rating
        except (ValueError, TypeError):
            return False

    def to_json_schema(self):
        """
        Converts the current RatingTag instance into a JSON Schema.

        Returns:
            dict: A dictionary representing the JSON Schema compatible with OpenAPI 3.
        """
        max_rating = int(self.attr.get('maxRating', 5))  # Default to 5 if not specified
        return {
            "type": "integer",
            "minimum": 0,
            "maximum": max_rating,
            "description": f"Rating for {self.to_name[0]} (0 to {max_rating})"
        }


class RelationsTag(ControlTag):
    """ """
    tag: str = "Relations"
    def validate_value(self, ) -> bool:
        """ """
        raise NotImplemented("""Should not be called directly, instead
        use validate_relation() method found in LabelInterface class""")

    def label(self, *args, **kwargs):
        """ """
        raise NotImplemented("""
        Relations work on regions instead of Object tags
        use Regions add_relation() method""")
        

class TaxonomyValue(BaseModel):
    taxonomy: List[List[str]]


class TaxonomyTag(ControlTag):
    """ """
    tag: str = "Taxonomy"
    _value_class: Type[TaxonomyValue] = TaxonomyValue
    _label_attr_name: str = "taxonomy"

    def _validate_value_labels(self, value):
        """Validate taxonomy labels by flattening selected paths before subset check.

        Expected value format:
          { "taxonomy": [["A"], ["A", "B"], ...] }
        """
        paths = value.get("taxonomy")
        if paths is None:
            return False
        if not isinstance(paths, list):
            return False
        flat_labels: List[str] = []
        for path in paths:
            if not isinstance(path, list):
                return False
            flat_labels.extend(path)
        return self._validate_labels(flat_labels)

    def to_json_schema(self):
        """
        Converts the current TaxonomyTag instance into a JSON Schema.

        Returns:
            dict: A dictionary representing the JSON Schema compatible with OpenAPI 3.
        """
        return {
            "type": "array",
            "items": {
                "type": "array",
                "items": {
                    "type": "string",
                    # TODO: enforce the order of the enums according to the taxonomy tree
                    "enum": self.labels
                }
            },
            "description": f"Taxonomy for {self.to_name[0]}. Each item is a path from root to selected node."
        }


class TextAreaValue(BaseModel):
    text: List[str]


class TextAreaTag(ControlTag):
    """ """
    tag: str = "TextArea"
    _value_class: Type[TextAreaValue] = TextAreaValue
    _label_attr_name: str = "text"

    def to_json_schema(self):
        """
        Converts the current TextAreaTag instance into a JSON Schema.

        Returns:
            dict: A dictionary representing the JSON Schema compatible with OpenAPI 3.
        """
        return {
            "oneOf": [
                {"type": "string"},
                {
                    "type": "array",
                    "items": {"type": "string"}
                }
            ],
            "description": f"Text or list of texts for {self.to_name[0]}"
        }



class TimeSeriesValue(SpanSelection):
    instant: bool
    timeserieslabels: List[str]


class TimeSeriesLabelsTag(ControlTag):
    """ """
    tag: str = "TimeSeriesLabels"
    _label_attr_name: str = "timeserieslabels"
    _value_class: Type[TimeSeriesValue] = TimeSeriesValue
