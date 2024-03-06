"""
"""

import xml.etree.ElementTree
from typing import Type, Dict, Optional, List, Tuple, Any, Union
from pydantic import BaseModel, confloat

from .base import LabelStudioTag
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


def get_tag_class(name):
    """ """
    class_name = _TAG_TO_CLASS.get(name.lower())
    return globals().get(class_name, None)


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

    @classmethod
    def parse_node(cls, tag: xml.etree.ElementTree.Element) -> "ControlTag":
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
        tag_class = get_tag_class(tag.tag) or cls

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

        if tag.attrib.get("value", "empty")[0] == "$" or tag.attrib.get("apiUrl"):
            tag_info["dynamic_value"] = True

        return tag_class(**tag_info)

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
        example when you're validate the annotaion or prediction to
        make sure there no undefined labels used.

        """
        if not self.labels:
            return True

        return set(labels).issubset(set(self.labels))

    def _validate_value_labels(self, value):
        """ """
        if self._label_attr_name not in value:
            return False

        return self._validate_labels(value.get(self._label_attr_name))

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
            if len(self.to_name) > 1:
                raise Exception(
                    "Multiple to_name in control tag, specify to_name in function"
                )

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
        This method creates a new Region object with the specified label applied.
        If not labels are provided, it creates a new instance of the value class with the provided arguments and keyword arguments.
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
        if hasattr(self, "_label_attr_name"):
            return self._label_with_labels(
                label=label, to_name=to_name, *args, **kwargs
            )
        else:
            return self._label_simple(to_name=to_name, *args, **kwargs)

    def as_tuple(self):
        """ """
        from_name = self.name
        to_name = self.to_name
        tag_type = self.tag

        if isinstance(to_name, list):
            to_name = ",".join(to_name)

        return "|".join([from_name, to_name, type.lower()])


class SpanSelection(BaseModel):
    start: str
    end: str


class SpanSelectionOffsets(SpanSelection):
    startOffset: int
    endOffset: int


class ChoicesValue(BaseModel):
    choices: List[str]


class ChoicesTag(ControlTag):
    """ """

    _label_attr_name: str = "choices"
    _value_class: Type[ChoicesValue] = ChoicesValue


class LabelsValue(SpanSelection):
    labels: List[str]


class LabelsTag(ControlTag):
    """ """

    _label_attr_name: str = "labels"
    _value_class: Type[LabelsValue] = LabelsValue


## Image tags


class BrushValue(BaseModel):
    format: str
    rle: List[int]


class BrushLabelsValue(BrushValue):
    brushlabels: List[str]


class BrushTag(ControlTag):
    """ """

    _value_class: Type[BrushValue] = BrushValue


class BrushLabelsTag(ControlTag):
    """ """

    _label_attr_name: str = "brushlabels"
    _value_class: Type[BrushLabelsValue] = BrushLabelsValue


class EllipseValue(BaseModel):
    x: confloat(le=100)
    y: confloat(le=100)
    radiusX: confloat(le=50)
    radiusY: confloat(le=50)
    rotation: confloat(le=360) = 0


class EllipseLabelsValue(EllipseValue):
    ellipselabels: List[str]


class EllipseTag(ControlTag):
    """ """

    _value_class: Type[EllipseValue] = EllipseValue


class EllipseLabelsTag(ControlTag):
    """ """

    _label_attr_name: str = "ellipselabels"
    _value_class: Type[EllipseLabelsValue] = EllipseLabelsValue


class KeyPointValue(BaseModel):
    x: confloat(le=100)
    y: confloat(le=100)


class KeyPointLabelsValue(KeyPointValue):
    keypointlabels: List[str]


class KeyPointTag(ControlTag):
    """ """

    _value_class: Type[KeyPointValue] = KeyPointValue


class KeyPointLabelsTag(ControlTag):
    """ """

    _label_attr_name: str = "keypointlabels"
    _value_class: Type[KeyPointLabelsValue] = KeyPointLabelsValue


class PolygonValue(BaseModel):
    points: Tuple[confloat(le=100), confloat(le=100)]


class PolygonLabelsValue(PolygonValue):
    polygonlabels: List[str]


class PolygonTag(ControlTag):
    """ """

    _value_class: Type[PolygonValue] = PolygonValue

    def label(self, *args, **kwargs):
        """ """


class PolygonLabelsTag(ControlTag):
    """ """

    _label_attr_name: str = "polygonlabels"
    _value_class: Type[PolygonLabelsValue] = PolygonLabelsValue


class RectangleValue(BaseModel):
    x: confloat(le=100)
    y: confloat(le=100)
    width: confloat(le=100)
    height: confloat(le=100)
    rotation: confloat(le=360)


class RectangleLabelsValue(RectangleValue):
    rectanglelabels: List[str]


class RectangleTag(ControlTag):
    """ """

    _value_class: Type[RectangleValue] = RectangleValue


class RectangleLabelsTag(ControlTag):
    """ """

    _label_attr_name: str = "rectanglelabels"
    _value_class: Type[RectangleLabelsValue] = RectangleLabelsValue


class VideoRectangleValue(BaseModel):
    x: float
    y: float
    width: float
    height: float
    rotation: float


class VideoRectangleTag(ControlTag):
    """ """

    _value_class: Type[VideoRectangleValue] = VideoRectangleValue


class NumberTag(ControlTag):
    """ """

    def validate_value(self, value) -> bool:
        """ """
        # TODO implement
        return True

    def label(self, *args, **kwargs):
        """ """


class DateTimeTag(ControlTag):
    """ """

    def validate_value(self, value) -> bool:
        """ """
        # TODO implement
        return True

    def label(self, *args, **kwargs):
        """ """


class HyperTextLabelsValue(SpanSelectionOffsets):
    htmllabels: List[str]


class HyperTextLabelsTag(ControlTag):
    """ """

    _label_attr_name: str = "htmllabels"
    _value_class: Type[HyperTextLabelsValue] = HyperTextLabelsValue


class PairwiseValue(BaseModel):
    selected: str


class PairwiseTag(ControlTag):
    """ """

    _value_class: Type[PairwiseValue] = PairwiseValue

    def label(self, *args, **kwargs):
        """ """


class ParagraphLabelsValue(SpanSelectionOffsets):
    paragraphlabels: List[str]


class ParagraphLabelsTag(ControlTag):
    """ """

    _label_attr_name: str = "paragraphlabels"
    _value_class: Type[ParagraphLabelsValue] = ParagraphLabelsValue

    def label(self, *args, **kwargs):
        """ """


class RankerTag(ControlTag):
    """ """

    def validate_value(self, value) -> bool:
        """ """
        # TODO
        return True

    def label(self, *args, **kwargs):
        """ """


class RatingValue(BaseModel):
    rating: int


class RatingTag(ControlTag):
    """ """

    _value_class: Type[RatingValue] = RatingValue

    def label(self, *args, **kwargs):
        """ """


class RelationsTag(ControlTag):
    """ """

    def validate_value(self, value) -> bool:
        """ """
        # TODO
        return True

    def label(self, *args, **kwargs):
        """ """


class TaxonomyValue(BaseModel):
    taxonomy: List[List[str]]


class TaxonomyTag(ControlTag):
    """ """

    _value_class: Type[TaxonomyValue] = TaxonomyValue


class TextAreaValue(BaseModel):
    text: List[str]


class TextAreaTag(ControlTag):
    """ """

    _value_class: Type[TextAreaValue] = TextAreaValue


class TimeSeriesValue(SpanSelection):
    instant: bool
    timeserieslabels: List[str]


class TimeSeriesLabelsTag(ControlTag):
    """ """

    _label_attr_name: str = "timeserieslabels"
    _value_class: Type[TimeSeriesValue] = TimeSeriesValue
