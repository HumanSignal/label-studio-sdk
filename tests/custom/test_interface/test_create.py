
import label_studio_sdk.label_interface.create as CE
from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.label_interface.control_tags import ChoicesTag
from label_studio_sdk.label_interface.object_tags import TextTag

NAME = "test_name"
SNAME = "second_name"
TNAME = "third_name"

CONVERT = [
    # convert string
    ("text", ("text", { "name": NAME, "value": "$" + NAME }, ())),

    # convert tuple
    (("text", { "name": NAME }), ("text", { "name": NAME, "value": "$" + NAME }, ())),
    (("text", { }), ("text", { "name": NAME, "value": "$" + NAME }, ())),

    # convert tag
    # (("text", { }), ("text", { "name": NAME, "value": "$"  NAME }, ()))
]

SIMPLE = [
    # lets convert a simple object tag
    ({ NAME: "text" }, [ ("text", { "name": NAME, "value": "$" + NAME }, ()) ]),

    # converting simple classification
    ({ NAME: "text", SNAME: "choices" },
     [ ("text", { "name": NAME, "value": "$" + NAME }, ()),
       ("choices", { "name": SNAME, "toName": NAME }, ()) ]),

    # convert with multiple object tags and verify toName connection
    ({ NAME: "text", TNAME: "text", SNAME: "choices" },
     [ ("text", { "name": NAME, "value": "$" + NAME }, ()),
       ("text", { "name": TNAME, "value": "$" + TNAME }, ()),
       ("choices", { "name": SNAME, "toName": NAME }, ()) ]),

    # make sure that name and toName are not not adjusted when used objects directly
    ({ NAME: TextTag(name="name", value="$val"), SNAME: ChoicesTag(name="cname", to_name=("name",)) },
     [ ("text", { "name": "name", "value": "$val" }, ()),
       ("choices", { "name": "cname", "toName": "name" }, ()) ])
]

def test_convert():
    """
    """
    for c in CONVERT:
        assert CE._convert(NAME, c[0]) == c[1]


def test_create_simple():
    for c in SIMPLE:
        assert CE.convert_tags_description(c[0]) == c[1]


def test_create_simple():
    """
    """
    # create_simple()
    assert CE.convert_tags_description({
        "text": "text",
        "chc": CE.choices(("one", "two"))
    }) == [ ('text', {'name': 'text', 'value': '$text'}, ()),
           ('Choices', {'name': 'chc', 'toName': 'text' }, (
               ('Choice', {'value': 'one'}, {}),
               ('Choice', {'value': 'two'}, {})
           )) ]


def test_create_taxonomy():
    label_names = ("1", "2", ("3", "4", ("5", "6")))
    res = CE.taxonomy(label_names)

    assert res == \
        ('Taxonomy',
        {},
        (('Choice', {'value': '1'}, {}),
            ('Choice', {'value': '2'}, {}),
            ('Choice',
                {'value': '3'},
                (('Choice', {'value': '4'}, {}), ('Choice', {'value': ('5', '6')}, {})))))


def test_create_image_labels():
    tag_type = "RectangleLabels"
    label_names = ("hello", "world")
    
    res = CE.labels(label_names, tag_type=tag_type)

    assert res[0] is tag_type
    assert len(res[2]) is len(label_names)


def test_using_lpi_tags():
    """ """
    tags = {
        'choices': ChoicesTag(name='sentiment_class', labels=['Positive', 'Negative', 'Neutral']),
        'input': TextTag(name='message', value='my_text'),
    }
    
    tuples = CE.convert_tags_description(tags, mapping=None)

    assert len(tags) is 2

    ftag = tuples[0]
    stag = tuples[1]

    assert ftag[0] == "Choices"
    assert stag[0] == "Text"    
    assert ftag[1]["name"] == "sentiment_class"
    assert ftag[1]["toName"] == "message"
    assert stag[1]["name"] == "message"
    assert stag[1]["value"] == '$my_text'

    tags = {
        'choices': ChoicesTag(labels=['Positive', 'Negative', 'Neutral']),
        'input': TextTag(),
    }

    tuples = CE.convert_tags_description(tags, mapping=None)
    ftag = tuples[0]
    stag = tuples[1]
    
    assert ftag[1]["name"] == "choices"
    assert ftag[1]["toName"] == "input"
    assert stag[1]["name"] == "input"
    assert stag[1]["value"] == "$input"


def test_create_instance_omits_missing_reactcode_value():
    """Rebuilding a ReactCode tag without ``value`` must preserve its data binding."""
    label_config = """
    <View>
      <ReactCode name="doc" toName="doc" data="$document" outputs='{"result":{"type":"string"}}'/>
    </View>
    """

    interface = LabelInterface(label_config)
    rebuilt_config = LabelInterface.create(tags={"doc": interface._objects["doc"]}, pretty=False)

    assert 'data="$document"' in rebuilt_config
    assert "value=" not in rebuilt_config
