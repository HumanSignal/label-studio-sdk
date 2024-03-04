"""
"""
from typing import Type, Dict, Optional, List, Tuple, Any, Union
from pydantic import BaseModel, confloat

from .base import LabelStudioTag
from .region import Region

_NOT_CONTROL_TAGS = {
    'Filter',
}

_TAG_TO_CLASS = {
    "choices": "ChoicesTag",
    "labels": "LabelsTag",
    "rectangle": "RectangleTag",
    "brush" : "BrushTag",
    "brushlabels" : "BrushLabelsTag",
    "ellipse" : "EllipseTag",
    "ellipselabels" : "EllipseLabelsTag",
    "keypoint" : "KeyPointTag",
    "keypointlabels" : "KeyPointLabelsTag",
    "polygon" : "PolygonTag",
    "polygonlabels" : "PolygonLabelsTag",
    "rectangle" : "RectangleTag",
    "rectanglelabels" : "RectangleLabelsTag",
    "videorectangle" : "VideoRectangleTag",
    "number" : "NumberTag",
    "datetime" : "DateTimeTag",
    "hypertext" : "HyperTextLabelsTag",
    "pairwise" : "PairwiseTag",
    "paragraphlabels" : "ParagraphLabelsTag",
    "ranker" : "RankerTag",
    "rating" : "RatingTag",
    "relations" : "RelationsTag",
    "taxonomy" : "TaxonomyTag",
    "textarea" : "TextAreaTag",
    "timeserieslabels" : "TimeSeriesLabelsTag",    
}

def get_tag_class(name):
    """
    """
    class_name = _TAG_TO_CLASS.get(name.lower())
    return globals().get(class_name, None)


class ControlTag(LabelStudioTag):
    """
    Class that represents a ControlTag in Label Studio
    """
    name: Optional[str] = None
    to_name: Optional[List[str]] = None
    conditionals: Optional[Dict[str, Any]] = None
    dynamic_value: Optional[bool] = False
    objects: Optional[Any] = None
    labels: Optional[Any] = None
    labels_attrs: Optional[Any] = None

    @classmethod
    def validate_node(cls, tag) -> bool:
        """
        Naive check if tag is a control tag
        """
        return bool(
            tag.attrib.get('name')
            and tag.attrib.get('toName')
            and tag.tag not in _NOT_CONTROL_TAGS
        )

    @classmethod
    def parse_node(cls, tag):
        """
        Parse tag into a tag info
        """
        tag_class = get_tag_class(tag.tag) or cls
        
        tag_info = {
            'tag': tag.tag,
            'name': tag.attrib['name'],
            'to_name': tag.attrib['toName'].split(','),
            'attr': tag.attrib
        }

        # Grab conditionals if any
        conditionals = {}
        if tag.attrib.get('perRegion') == 'true':
            if tag.attrib.get('whenTagName'):
                conditionals = {'type': 'tag', 'name': tag.attrib['whenTagName']}
            elif tag.attrib.get('whenLabelValue'):
                conditionals = {
                    'type': 'label',
                    'name': tag.attrib['whenLabelValue'],
                }
            elif tag.attrib.get('whenChoiceValue'):
                conditionals = {
                    'type': 'choice',
                    'name': tag.attrib['whenChoiceValue'],
                }
                        
        if conditionals:
            tag_info['conditionals'] = conditionals
            
        if tag.attrib.get("value", "empty")[0] == "$" or \
           tag.attrib.get("apiUrl"):
            tag_info['dynamic_value'] = True

        return tag_class(**tag_info)
    
    def get_object(self, name=None):
        """
        """
        return self.get_input(name=name);
        
    def get_input(self, name=None):
        """Returns the object tag that control tag maps to
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
        """
        self.labels_attrs = labels_attrs

    def set_object(self, tag):
        """
        """
        self.objects = [ tag ]
        
    def set_objects(self, objects):
        """
        """
        self.objects = objects

    def set_labels(self, labels: List[str]):
        """
        Set labels for the ControlTag
        """
        self.labels = labels

    def find_object_by_name(self, name):
        """
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
        """
        """
        if self._label_attr_name not in value:
            return False
        
        return self._validate_labels(value.get(self._label_attr_name))        
    
    def validate_value(self, value: dict) -> bool:
        """Validate a value of the tag. This method first checks if
        _label_attr_name is defined. If it is, it calls
        _validate_value_labels to validate labels of value with the
        ones defined in the tag. If labels are not valid, it returns
        False. Then it tries to instantiate self._value_class which is
        a pydantic definition of the structure of value. If
        instantiation fails, it returns False, otherwise returns True.
        
        :param value: Value to be validated
        :type value: dict

        :return : True if value is valid; otherwise, False
        :rtype : bool
        """
        if hasattr(self, "_label_attr_name"):
            if not self._validate_value_labels(value):
                return False
        
        try:
            inst = self._value_class(**value)
            return True
        except Exception as e:
            return False
    
    def _resolve_to_name(self, to_name):
        """
        """
        if to_name:
            if to_name not in self.to_name:
                raise Exception("To name is not found in control tag")

            return to_name
        else:
            if len(self.to_name) > 1:
                raise Exception("Multiple to_name in control tag, specify to_name in function")
            
            return self.to_name[0]        

    def _label_simple(self, to_name=None, *args, **kwargs):
        """
        """        
        to_name = self._resolve_to_name(to_name)
        obj = self.find_object_by_name(to_name)
        cls = self._value_class
        value = cls(**kwargs)
        
        return Region(from_tag=self, to_tag=obj, value=value)
        
    def _label_with_labels(self, label=None, to_name=None, *args, **kwargs):
        """
        """
        if isinstance(label, str):
            label = [ label ]

        if not self._validate_labels(label):
            raise Exception(f"Using labels not defined in labeling config, possible values: {set(self.labels)}")

        kwargs[self._label_attr_name] = label
        
        return self._label_simple(to_name=to_name, **kwargs)        

    def label(self, label=None, to_name=None, *args, **kwargs):
        """This method serves as a general interface for the labeling
        process. If the `self._label_attr_name` attribute exists in
        the current object, it labels the object with labels by
        calling `self._label_with_labels()`. If not, it labels the
        object simple by calling `self._label_simple()`.

        :param to_name: The name of the object
        :type to_name: str, optional
        :param label: The label to be applied
        :type label: str or list of strings, optional

        :return : A new Region object with the specified label applied.
        """
        if hasattr(self, "_label_attr_name"):
            return self._label_with_labels(label=label, to_name=to_name, *args, **kwargs)
        else:
            return self._label_simple(to_name=to_name, *args, **kwargs)    
        
    def as_tuple(self):
        """
        """
        from_name = self.name
        to_name = self.to_name
        tag_type = self.tag
        
        if isinstance(to_name, list):
            to_name = ','.join(to_name)
            
        return '|'.join([from_name, to_name, type.lower()])

    
class SpanSelection(BaseModel):
    start: str
    end: str

    
class SpanSelectionOffsets(SpanSelection):
    startOffset: int
    endOffset: int

    
class ChoicesValue(BaseModel):
    choices: List[str]


class ChoicesTag(ControlTag):
    """
    """    
    _label_attr_name: str = "choices"
    _value_class: Type[ChoicesValue] = ChoicesValue
    
    
class LabelsValue(SpanSelection):
    labels: List[str]
        
        
class LabelsTag(ControlTag):
    """
    """    
    _label_attr_name: str = "labels"
    _value_class: Type[LabelsValue] = LabelsValue
    
## Image tags

class BrushValue(BaseModel):
    format: str
    rle: List[int]

class BrushLabelsValue(BrushValue):
    brushlabels: List[str]

class BrushTag(ControlTag):
    """
    """
    _value_class: Type[BrushValue] = BrushValue

        
class BrushLabelsTag(ControlTag):
    """
    """
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
    """
    """
    _value_class: Type[EllipseValue] = EllipseValue


class EllipseLabelsTag(ControlTag):
    """
    """
    _label_attr_name: str = "ellipselabels"
    _value_class: Type[EllipseLabelsValue] = EllipseLabelsValue


class KeyPointValue(BaseModel):
    x: confloat(le=100)
    y: confloat(le=100)

class KeyPointLabelsValue(KeyPointValue):
    keypointlabels: List[str]
    
        
class KeyPointTag(ControlTag):
    """
    """
    _value_class: Type[KeyPointValue] = KeyPointValue

        
class KeyPointLabelsTag(ControlTag):
    """
    """
    _label_attr_name: str = "keypointlabels"
    _value_class: Type[KeyPointLabelsValue] = KeyPointLabelsValue


class PolygonValue(BaseModel):
    points: Tuple[confloat(le=100), confloat(le=100)]

class PolygonLabelsValue(PolygonValue):
    polygonlabels: List[str]


class PolygonTag(ControlTag):
    """
    """
    _value_class: Type[PolygonValue] = PolygonValue
                
    def label(self, *args, **kwargs):
        """
        """
        
class PolygonLabelsTag(ControlTag):
    """
    """
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
    """
    """
    _value_class: Type[RectangleValue] = RectangleValue
    

class RectangleLabelsTag(ControlTag):
    """
    """
    _label_attr_name: str = "rectanglelabels"
    _value_class: Type[RectangleLabelsValue] = RectangleLabelsValue
    
        
class VideoRectangleValue(BaseModel):
    x: float
    y: float
    width: float
    height: float
    rotation: float

        
class VideoRectangleTag(ControlTag):
    """
    """
    _value_class: Type[VideoRectangleValue] = VideoRectangleValue


class NumberTag(ControlTag):
    """
    """    
    def validate_value(self, value) -> bool:
        """
        """
        # TODO implement
        return True

    def label(self, *args, **kwargs):
        """
        """


class DateTimeTag(ControlTag):
    """
    """
    def validate_value(self, value) -> bool:
        """
        """
        # TODO implement
        return True

    def label(self, *args, **kwargs):
        """
        """
    
        
class HyperTextLabelsValue(SpanSelectionOffsets):    
    htmllabels: List[str]

        
class HyperTextLabelsTag(ControlTag):
    """
    """
    _label_attr_name: str = "htmllabels"
    _value_class: Type[HyperTextLabelsValue] = HyperTextLabelsValue


class PairwiseValue(BaseModel):
    selected: str

        
class PairwiseTag(ControlTag):
    """
    """
    _value_class: Type[PairwiseValue] = PairwiseValue

    def label(self, *args, **kwargs):
        """
        """


class ParagraphLabelsValue(SpanSelectionOffsets):
    paragraphlabels: List[str]
    
        
class ParagraphLabelsTag(ControlTag):
    """
    """
    _label_attr_name: str = "paragraphlabels"
    _value_class: Type[ParagraphLabelsValue] = ParagraphLabelsValue

    def label(self, *args, **kwargs):
        """
        """

        
class RankerTag(ControlTag):
    """
    """
    def validate_value(self, value) -> bool:
        """
        """
        # TODO
        return True

    def label(self, *args, **kwargs):
        """
        """

        
class RatingValue(BaseModel):
    rating: int

        
class RatingTag(ControlTag):
    """
    """
    _value_class: Type[RatingValue] = RatingValue

    def label(self, *args, **kwargs):
        """
        """    
        
                
class RelationsTag(ControlTag):
    """
    """
    def validate_value(self, value) -> bool:
        """
        """
        # TODO
        return True    

    def label(self, *args, **kwargs):
        """
        """

class TaxonomyValue(BaseModel):
    taxonomy: List[List[str]]

        
class TaxonomyTag(ControlTag):
    """
    """
    _value_class: Type[TaxonomyValue] = TaxonomyValue
    
        
class TextAreaValue(BaseModel):
    text: List[str]

        
class TextAreaTag(ControlTag):
    """
    """
    _value_class: Type[TextAreaValue] = TextAreaValue


class TimeSeriesValue(SpanSelection):
    instant: bool
    timeserieslabels: List[str]

        
class TimeSeriesLabelsTag(ControlTag):
    """
    """
    _label_attr_name: str = "timeserieslabels"
    _value_class: Type[TimeSeriesValue] = TimeSeriesValue
