from label_studio_sdk.label_interface.region import Region
from label_studio_sdk.label_interface.object_tags import ImageTag
from label_studio_sdk.label_interface.control_tags import RectangleTag, ReactCodeTag


def test_li():
    """Test using Label Interface to label things
    """
    img = ImageTag(
        name="img", tag="image", value="http://example.com/image.jpg", attr={}
    )
    rect = RectangleTag(name="rect", to_name=["img"], tag="rectangle", attr={})
    rect.set_object(img)

    region = rect.label(x=10, y=10, width=10, height=10, rotation=10)

    assert isinstance(region, Region)
    assert region._dict()["to_name"] == "img"
    assert region._dict()["from_name"] == "rect"


def test_find_tags_by_class():
    """Test finding tags by class type in Label Interface.
    
    This test validates:
    - Creating a LabelInterface with multiple tag types
    - Using find_tags_by_class to filter tags by their class
    - Verifying that only tags of the specified class are returned
    - Ensuring the method works with ReactCode tag
    """
    from label_studio_sdk.label_interface import LabelInterface
    
    # Setup: Create a config with multiple tag types including ReactCode
    config = """
    <View>
        <Image name="img" value="$image"/>
        <Rectangle name="rect" toName="img"/>
        <ReactCode name="react1" toName="react1" value="$my_data1" outputs="field1, field2" />
        <ReactCode name="react2" toName="react2" value="$my_data2" outputs="field3, field4"><![CDATA[
        function MyInterface({ React, addRegion, regions, data }) {
          return React.createElement('div', {}, 'content');
        }
        ]]></ReactCode>
        <Choices name="choice" toName="img">
            <Choice value="option1"/>
            <Choice value="option2"/>
        </Choices>
    </View>
    """
    
    # Action: Parse the config and find tags by class
    li = LabelInterface(config)
    
    # Validation: Find all ReactCodeTag instances
    react_code_tags = li.find_tags_by_class(ReactCodeTag)
    
    # Verify we found exactly 2 ReactCode tags
    assert len(react_code_tags) == 2, f"Expected 2 ReactCode tags, found {len(react_code_tags)}"
    
    # Verify all returned tags are ReactCodeTag instances
    for tag in react_code_tags:
        assert isinstance(tag, ReactCodeTag), f"Expected ReactCodeTag, got {type(tag)}"
    
    # Verify the names match
    tag_names = [tag.name for tag in react_code_tags]
    assert "react1" in tag_names, "Expected to find 'react1' tag"
    assert "react2" in tag_names, "Expected to find 'react2' tag"

