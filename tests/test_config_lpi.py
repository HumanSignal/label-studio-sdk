
from label_studio_sdk.label_config.region import Region
from label_studio_sdk.label_config.object_tags import ImageTag
from label_studio_sdk.label_config.control_tags import RectangleTag

def test_config_lpi():
    """
    """
    img = ImageTag(name="img", tag="image", value="http://example.com/image.jpg", attr={})
    rect = RectangleTag(name="rect", to_name=["img"], tag="rectangle", attr={})
    rect.set_object(img)
    
    rect.label(x=10, y=10,
               width=10, height=10,
               rotation=10)

    
