"""
"""

import json
import os
import re
import xml.etree.ElementTree
from urllib.parse import urlencode
from typing import Optional

from .base import LabelStudioTag, get_tag_class

_TAG_TO_CLASS = {
    "audio": "AudioTag",
    "image": "ImageTag",
    "table": "TableTag",
    "text": "TextTag",
    "video": "VideoTag",
    "hypertext": "HyperTextTag",
    "list": "ListTag",
    "paragraphs": "ParagraphsTag",
    "timeseries": "TimeSeriesTag",
}

_DATA_EXAMPLES = None


def _is_strftime_string(s):
    """simple way to detect strftime format"""
    return "%" in s


def generate_time_series_json(time_column, value_columns, time_format=None):
    """Generate sample for time series"""
    import numpy as np

    n = 100
    if time_format is not None and not _is_strftime_string(time_format):
        time_fmt_map = {"yyyy-MM-dd": "%Y-%m-%d"}
        time_format = time_fmt_map.get(time_format)

    if time_format is None:
        times = np.arange(n).tolist()
    else:
        raise NotImplementedError(
            "time_format is not implemented yet - you need to install pandas for this."
        )
        # import pandas as pd
        # times = pd.date_range('2020-01-01', periods=n, freq='D').strftime(time_format).tolist()
    ts = {time_column: times}
    for value_col in value_columns:
        ts[value_col] = np.random.randn(n).tolist()
    return ts


def data_examples(
    mode: str = "upload", hostname: str = "http://localhost:8080"
) -> dict:
    """Data examples for editor preview and task upload examples"""
    global _DATA_EXAMPLES

    if _DATA_EXAMPLES is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "data_examples.json")

        with open(file_path, encoding="utf-8") as f:
            _DATA_EXAMPLES = json.load(f)

        roots = ["editor_preview", "upload"]
        for root in roots:
            for key, value in _DATA_EXAMPLES[root].items():
                if isinstance(value, str):
                    _DATA_EXAMPLES[root][key] = value.replace(
                        "<HOSTNAME>", hostname
                    )  # TODO settings.HOSTNAME

    return _DATA_EXAMPLES[mode]


class ObjectTag(LabelStudioTag):
    """
    Class that represents a ObjectTag in Label Studio

    Attributes:
    -----------
    name: Optional[str]
        The name of the tag
    value: Optional[str]
        The value of the tag
    """

    name: Optional[str] = None
    value: Optional[str] = None
    # value_type: Optional[str] = None,

    # TODO needs to set during parsing
    # self._value_type = value_type

    @classmethod
    def parse_node(cls, tag: xml.etree.ElementTree.Element, tags_mapping=None) -> "ObjectTag":
        """
        This class method parses a node and returns a ObjectTag object if the node has a name and a value.

        Parameters:
        -----------
        tag : xml.etree.ElementTree.Element
            The node to be parsed.

        Returns:
        --------
        ObjectTag
            A new ObjectTag object with the tag name, attributes, name, and value.
        """
        tag_class = get_tag_class(tag.tag, _TAG_TO_CLASS, re_mapping=tags_mapping) or cls
        if isinstance(tag_class, str):
            tag_class = globals().get(tag_class, None)
        
        return tag_class(
            tag=tag.tag,
            attr=dict(tag.attrib),
            name=tag.attrib.get("name"),
            value=tag.attrib.get('valueList', tag.attrib.get('value')),
        )

    @classmethod
    def validate_node(cls, tag: xml.etree.ElementTree.Element) -> bool:
        """
        Check if tag is input
        """
        return bool(tag.attrib.get("name") and (tag.attrib.get("value") or tag.attrib.get("valueList")))

    @property
    def value_type(self):
        return self.attr.get("valueType") or self.attr.get("valuetype")

    @property
    def value_name(self):
        """ """
        # TODO this needs a check for URL
        return self.value[1:]

    @property
    def value_is_variable(self) -> bool:
        """Check if value has variable"""
        pattern = re.compile(r"^\$[^, ]+$")
        return bool(pattern.fullmatch(self.value))

    def collect_attrs(self):
        """Return tag attrs as a single dict"""
        return {
            **self.attr,
            "name": self.name,
            "value": '$' + self.value if self.value is not None else None
        }

    # and have generate_example in each
    def generate_example_value(self, mode="upload", secure_mode=False):
        """ """
        examples = data_examples(mode=mode)
        only_urls = secure_mode or self.value_type == "url"
        if hasattr(self, "_generate_example"):
            return self._generate_example(examples, only_urls=only_urls)
        example_from_field_name = examples.get("$" + self.value, None)
        if example_from_field_name:
            return example_from_field_name

        if self.tag.lower().endswith("labels"):
            return examples["Labels"]

        if self.tag.lower() == "choices":
            allow_nested = (
                self.attr.get("allowNested") or self.attr.get("allownested") or "false"
            )
            return examples["NestedChoices" if allow_nested == "true" else "Choices"]

        # patch for valueType="url"
        examples["Text"] = examples["TextUrl"] if only_urls else examples["TextRaw"]
        # not found by name, try get example by type
        return examples.get(self.tag, "Something")


class AudioTag(ObjectTag):
    """ """
    tag: str = "Audio"
    
    def _generate_example(self, examples, only_urls=False):
        """ """
        return examples.get("Audio")


class ImageTag(ObjectTag):
    """Image tag"""
    tag: str = "Image"
    
    def _generate_example(self, examples, only_urls=False):
        """ """
        return examples.get("Image")
    
    @property
    def is_image_list(self):
        """Check if the tag is an image list, i.e. it has a valueList attribute that accepts list of images"""
        return bool(self.attr.get("valueList")) if self.attr else False


class TableTag(ObjectTag):
    """ """
    tag: str = "Table"
    
    def _generate_example(self, examples, only_urls=False):
        """ """
        return examples.get("Table")


class TextTag(ObjectTag):
    """ """
    tag: str = "Text"
    
    def _generate_example(self, examples, only_urls=False):
        """ """
        if only_urls:
            return examples.get("TextUrl")
        else:
            return examples.get("TextRaw")


class VideoTag(ObjectTag):
    """ """
    tag: str = "Video"
    
    def _generate_example(self, examples, only_urls=False):
        """ """
        return examples.get("Video")


class HyperTextTag(ObjectTag):
    """ """
    tag: str = "HyperText"
    
    def _generate_example(self, examples, only_urls=False):
        """ """
        examples = data_examples(mode="upload")
        if self.value == "video":
            return examples.get("$videoHack")
        else:
            return examples["HyperTextUrl" if only_urls else "HyperText"]


class ListTag(ObjectTag):
    """ """
    tag: str = "List"
    
    def _generate_example(self, examples, only_urls=False):
        """ """
        examples = data_examples(mode="upload")
        return examples.get("List")


class ParagraphsTag(ObjectTag):
    """ """
    tag: str = "Paragraphs"
    
    def _generate_example(self, examples, only_urls=False):
        """ """
        # Paragraphs special case - replace nameKey/textKey if presented
        p = self.attr

        name_key = p.get("nameKey") or p.get("namekey") or "author"
        text_key = p.get("textKey") or p.get("textkey") or "text"

        if only_urls:
            params = {"nameKey": name_key, "textKey": text_key}
            return examples.get("ParagraphsUrl") + urlencode(params)

        return [
            {name_key: item["author"], text_key: item["text"]}
            for item in examples.get("Paragraphs")
        ]


class TimeSeriesTag(ObjectTag):
    """ """
    tag: str = "TimeSeries"
    
    def _generate_example(self, examples, only_urls=False):
        """ """
        p = self.attr

        time_column = p.get("timeColumn", "time")
        value_columns = []
        for ts_child in p:
            if ts_child.tag != "Channel":
                continue
            value_columns.append(ts_child.get("column"))
        sep = p.get("sep")
        time_format = p.get("timeFormat")

        if only_urls:
            # data is URL
            params = {"time": time_column, "values": ",".join(value_columns)}
            if sep:
                params["sep"] = sep
            if time_format:
                params["tf"] = time_format

            return "/samples/time-series.csv?" + urlencode(params)
        else:
            # data is JSON
            return generate_time_series_json(time_column, value_columns, time_format)
