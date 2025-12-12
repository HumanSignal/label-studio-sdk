from label_studio_sdk.label_interface.region import Region
from label_studio_sdk.label_interface.object_tags import ImageTag
from label_studio_sdk.label_interface.control_tags import RectangleTag, CustomInterfaceTag


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
    - Ensuring the method works with CustomInterfaceTag
    """
    from label_studio_sdk.label_interface import LabelInterface
    
    # Setup: Create a config with multiple tag types including CustomInterface
    config = """
    <View>
        <Image name="img" value="$image"/>
        <Rectangle name="rect" toName="img"/>
        <CustomInterface name="custom1" toName="custom1" value="$my_data1" outputs="field1, field2" />
        <CustomInterface name="custom2" toName="custom2" value="$my_data2" outputs="field3, field4"><![CDATA[
        function MyInterface({ React, addRegion, regions, data }) {
          return React.createElement('div', {}, 'content');
        }
        ]]></CustomInterface>
        <Choices name="choice" toName="img">
            <Choice value="option1"/>
            <Choice value="option2"/>
        </Choices>
    </View>
    """
    
    # Action: Parse the config and find tags by class
    li = LabelInterface(config)
    
    # Validation: Find all CustomInterfaceTag instances
    custom_tags = li.find_tags_by_class(CustomInterfaceTag)
    
    # Verify we found exactly 2 CustomInterface tags
    assert len(custom_tags) == 2, f"Expected 2 CustomInterface tags, found {len(custom_tags)}"
    
    # Verify all returned tags are CustomInterfaceTag instances
    for tag in custom_tags:
        assert isinstance(tag, CustomInterfaceTag), f"Expected CustomInterfaceTag, got {type(tag)}"
    
    # Verify the names match
    tag_names = [tag.name for tag in custom_tags]
    assert "custom1" in tag_names, "Expected to find 'custom1' tag"
    assert "custom2" in tag_names, "Expected to find 'custom2' tag"

