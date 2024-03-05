FROM_NAME = "from_name"
FROM_NAME_PREFIX = "from"
TO_NAME = "to_name"
ANOTHER_NAME = "another_name"
ANOTHER_TO_NAME = "another_to_name"

VALUE = "$var"
VALUE_KEY = "var"
ANOTHER_VALUE = "$var2"

LABEL1 = "yes"
LABEL2 = "no"

CORRECT_TASK = {VALUE_KEY: "value"}

CORRECT_REGION = {
    "from_name": FROM_NAME,
    "to_name": TO_NAME,
    "type": "choices",
    "value": {"choices": [LABEL1]},
}

SIMPLE_CONF = f"""
    <View>
      <Text name="{TO_NAME}" value="{VALUE}" />      
      <Choices name="{FROM_NAME}" toName="{TO_NAME}">
        <Choice value="{LABEL1}" />
        <Choice value="{LABEL2}" />
      </Choices>
    </View>
"""

SIMPLE_WRONG_CONF = f"""
    <View>
      <Text name="{TO_NAME}" value="{VALUE}" />
      <Text name="{TO_NAME}" value="{VALUE}" />
      <Choices name="{FROM_NAME}" toName="{ANOTHER_TO_NAME}">
        <Choice value="{LABEL1}" />
        <Choice value="{LABEL2}" />
      </Choices>
    </View>
"""

CONF_WITH_COMMENT = (
    '<!-- {"data": { "hello": "world" }, "predictions": [], "annotations": [] } -->'
    + f"""{SIMPLE_CONF}"""
)

CONF_COMPLEX = f"""
<View>
  <Labels name="label" toName="text">
    <Label value="PER" background="red"/>
    <Label value="ORG" background="darkorange"/>
    <Label value="LOC" background="orange"/>
    <Label value="MISC" background="green"/>
  </Labels>

  <Text name="text" value="$text"/>
  <Choices name="sentiment" toName="text"
             choice="single" showInLine="true">
      <Choice value="Positive"/>
      <Choice value="Negative"/>
      <Choice value="Neutral"/>
    </Choices>
</View>
"""

TWO_TONAMES = f"""
    <View>
      <Text name="{TO_NAME}" value="{VALUE}" />
      <Text name="{ANOTHER_TO_NAME}" value="{VALUE}" />
      <Choices name="{FROM_NAME}" toName="{TO_NAME},{ANOTHER_TO_NAME}">
        <Choice value="{LABEL1}" />
        <Choice value="{LABEL2}" />
      </Choices>
    </View>
"""

TEXTAREA_CONF = f"""
<View>
  <Textarea name="{FROM_NAME}" toName="{TO_NAME}" />
  <Text name="{TO_NAME}" value="{VALUE}" />

  <Choices name="{ANOTHER_NAME}" toName="{TO_NAME}">
    <Choice value="{LABEL1}" />
    <Choice value="{LABEL2}" />
  </Choices>
</View>
"""

VIDEO_CONF = f"""
<View>
  <Labels name="videoLabels" toName="video">
    <Label value="Car"/>
    <Label value="Person"/>
  </Labels>
  <Video name="video" value="$video"/>
  <VideoRectangle name="box" toName="video"/>
</View>
"""

NO_DYNAMIC_LABELS_CONF = f"""
<View>
  <Header value="Select label and click the image to start"/>
  <Image name="image" value="$image" zoom="true"/>
  <PolygonLabels name="label" toName="image"
     strokeWidth="3" pointSize="small"
     opacity="0.9" />
</View>
"""

DYNAMIC_LABELS_CONF = f"""
<View>
  <Header value="Select label and click the image to start"/>
  <Image name="image" value="$image" zoom="true"/>
  <PolygonLabels name="label" toName="image"
     strokeWidth="3" pointSize="small"
     opacity="0.9" value="$options" />
</View>
"""

RECT_CONFIG = f"""
<View>
  <Image name="{TO_NAME}" value="{VALUE}" />
  <Rectangle name="{FROM_NAME}" toName="{TO_NAME}"></Rectangle>
</View>
"""
