"""
"""
import re
import os
import json

from typing import Dict, Optional, List, Tuple, Any
from .base import LabelStudioTag
from .region import Region

_TAG_TO_CLASS = {
    "audio":"AudioTag",
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
    """simple way to detect strftime format
    """
    return '%' in s

def generate_time_series_json(time_column, value_columns, time_format=None):
    """Generate sample for time series
    """
    n = 100
    if time_format is not None and not _is_strftime_string(time_format):
        time_fmt_map = {'yyyy-MM-dd': '%Y-%m-%d'}
        time_format = time_fmt_map.get(time_format)

    if time_format is None:
        times = np.arange(n).tolist()
    else:
        times = pd.date_range('2020-01-01', periods=n, freq='D').strftime(time_format).tolist()
    ts = {time_column: times}
    for value_col in value_columns:
        ts[value_col] = np.random.randn(n).tolist()
    return ts    

def data_examples(mode, hostname="https://example.com/"):
    """Data examples for editor preview and task upload examples"""
    global _DATA_EXAMPLES

    if _DATA_EXAMPLES is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'data_examples.json')
        
        with open(file_path, encoding='utf-8') as f:
            _DATA_EXAMPLES = json.load(f)

        roots = ['editor_preview', 'upload']
        for root in roots:
            for key, value in _DATA_EXAMPLES[root].items():
                if isinstance(value, str):
                    _DATA_EXAMPLES[root][key] = value.replace('<HOSTNAME>', hostname) # TODO settings.HOSTNAME

    return _DATA_EXAMPLES[mode]

def get_tag_class(name):
    """
    """
    class_name = _TAG_TO_CLASS.get(name.lower())
    return globals().get(class_name, None)


class ObjectTag(LabelStudioTag):
    """
    Class that represents a ObjectTag in Label Studio
    """
    name: Optional[str] = None
    value: Optional[str] = None
    # value_type: Optional[str] = None,

    # TODO needs to set during parsing
    # self._value_type = value_type

    @classmethod
    def parse_node(cls, tag) -> 'ObjectTag':
        """
        """
        tag_class = get_tag_class(tag.tag) or cls
        
        return tag_class(tag=tag.tag, attr=tag.attrib,
                         name=tag.attrib.get('name'),
                         value=tag.attrib['value'])

    @classmethod
    def validate_node(cls, tag) -> bool:
        """
        Check if tag is input
        """
        return bool(tag.attrib.get('name') and tag.attrib.get('value'))

    @property
    def value_type(self):
        p = self.attr
        return p.get('valueType') or p.get('valuetype')

    @property
    def value_name(self):
        """
        """
        # TODO this needs a check for URL
        return self.value[1:]    
    
    @property
    def value_is_variable(self) -> bool:
        """Check if value has variable
        """
        pattern = re.compile(r"^\$[A-Za-z_]+$")
        return bool(pattern.fullmatch(self.value))    
    
    # TODO this should not be here as soon as we cover all the tags
    # and have generate_example in each
    def generate_example_value(self, mode="upload", secure_mode=False):
        """
        """
        examples = data_examples(mode=mode)
        only_urls = secure_mode or self.value_type == 'url'
        
        if hasattr(self, "generate_example"):
            return self.generate_example(only_urls=only_urls)
        
        example_from_field_name = examples.get('$' + self.value, None)
        if example_from_field_name:
            return example_from_field_name
        
        if self.tag.lower().endswith('labels'):
            return examples['Labels']

        if self.tag.lower() == 'choices':
            allow_nested = self.attr.get('allowNested') or self.attr.get('allownested') or 'false'
            return examples['NestedChoices' if allow_nested == 'true' else 'Choices']

        # patch for valueType="url"
        examples['Text'] = examples['TextUrl'] if only_urls else examples['TextRaw']
        # not found by name, try get example by type
        return examples.get(self.tag, 'Something')


class AudioTag(ObjectTag):
    """
    """
    def generate_example(self, only_urls=False):
        """
        """
        return examples.get('List')
    
class ImageTag(ObjectTag):
    """
    """
    def generate_example(self, only_urls=False):
        """
        """
        return examples.get('List')
    
class TableTag(ObjectTag):
    """
    """
    def generate_example(self, only_urls=False):
        """
        """
        return examples.get('List')
    
    
class TextTag(ObjectTag):
    """
    """
    def generate_example(self, only_urls=False):
        """
        """
        if only_urls:
            return "https://htx-pub.s3.amazonaws.com/example.txt"
        else:
            return "To have faith is to trust yourself to the water"

    
class VideoTag(ObjectTag):
    """
    """
    def generate_example(self, only_urls=False):
        """
        """
        return examples.get('List')

    
class HyperTextTag(ObjectTag):
    """
    """
    def generate_example(self, only_urls=False):
        """
        """
        if self.value == 'video':
            return examples.get('$videoHack')
        else:
            return examples['HyperTextUrl' if only_urls else 'HyperText']


class ListTag(ObjectTag):
    """
    """
    def generate_example(self, only_urls=False):
        """
        """
        return examples.get('List')


class ParagraphsTag(ObjectTag):
    """
    """
    def generate_example(self, only_urls=False):
        """
        """
        # Paragraphs special case - replace nameKey/textKey if presented
        name_key = p.get('nameKey') or p.get('namekey') or 'author'
        text_key = p.get('textKey') or p.get('textkey') or 'text'
        
        if only_urls:
            params = {'nameKey': name_key, 'textKey': text_key}
            return examples['ParagraphsUrl'] + urlencode(params)

        return [{ name_key: item['author'], text_key: item['text'] }
                for item in examples[p.tag]]


class TimeSeriesTag(ObjectTag):
    """
    """
    def generate_example(self):
        """
        """
        time_column = self.attr.get('timeColumn')
        value_columns = []
        for ts_child in p:
            if ts_child.tag != 'Channel':
                continue
            value_columns.append(ts_child.get('column'))
        sep = p.get('sep')
        time_format = p.get('timeFormat')

        if only_urls:
            # data is URL
            params = {'time': time_column, 'values': ','.join(value_columns)}
            if sep:
                params['sep'] = sep
            if time_format:
                params['tf'] = time_format
            task[value] = '/samples/time-series.csv?' + urlencode(params)
        else:
            # data is JSON
            task[value] = generate_time_series_json(time_column, value_columns, time_format)
