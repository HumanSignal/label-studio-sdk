
from label_studio_sdk.label_interface.region import Region
from label_studio_sdk.label_interface.object_tags import ImageTag
from label_studio_sdk.label_interface.control_tags import RectangleTag

def test_li():
    """Test using Label Interface to label things
    """
    img = ImageTag(name="img", tag="image", value="http://example.com/image.jpg", attr={})
    rect = RectangleTag(name="rect", to_name=["img"], tag="rectangle", attr={})
    rect.set_object(img)
    
    region = rect.label(x=10, y=10,
                        width=10, height=10,
                        rotation=10)

    

    
