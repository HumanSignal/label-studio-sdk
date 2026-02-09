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
      <Text name="{ANOTHER_TO_NAME}" value="{ANOTHER_VALUE}" />
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
  <Labels name="videoLabels" toName="{TO_NAME}" >
    <Label value="{LABEL1}" />
    <Label value="{LABEL2}" />
  </Labels>
  <Video name="{TO_NAME}" value="{VALUE}" />
  <VideoRectangle name="{FROM_NAME}" toName="{TO_NAME}" />
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

EMPTY_VALUE_CONF = f"""
<View>
  <Text name="text" value="$text"/>
  <Labels name="type" toName="text">
    <Label value="" />
    <Label value="" />
  </Labels>
</View>
"""

NO_VALUE_CONF = f"""
<View>
  <Text name="text" value="$text"/>
  <Labels name="type" toName="text">
    <Label />
    <Label value="" />
  </Labels>
</View>
"""

# Prediction validation test configurations
PREDICTION_CHOICES_CONFIG = """
<View>
  <Text name="text" value="$text"/>
  <Choices name="choices" toName="text">
    <Choice value="choice1"/>
    <Choice value="choice2"/>
    <Choice value="choice3"/>
  </Choices>
</View>
"""

PREDICTION_LABELS_CONFIG = """
<View>
  <Text name="text" value="$text"/>
  <Labels name="labels" toName="text">
    <Label value="label1" background="red"/>
    <Label value="label2" background="blue"/>
    <Label value="label3" background="green"/>
  </Labels>
</View>
"""

PREDICTION_BRUSH_CONFIG = """
<View>
  <Image name="image" value="$image"/>
  <Brush name="brush" toName="image" strokeWidth="5"/>
</View>
"""

PREDICTION_BRUSH_LABELS_CONFIG = """
<View>
  <Image name="image" value="$image"/>
  <BrushLabels name="brushlabels" toName="image" strokeWidth="5">
    <Label value="brush1" background="red"/>
    <Label value="brush2" background="blue"/>
  </BrushLabels>
</View>
"""

PREDICTION_ELLIPSE_CONFIG = """
<View>
  <Image name="image" value="$image"/>
  <Ellipse name="ellipse" toName="image"/>
</View>
"""

PREDICTION_ELLIPSE_LABELS_CONFIG = """
<View>
  <Image name="image" value="$image"/>
  <EllipseLabels name="ellipselabels" toName="image">
    <Label value="ellipse1" background="red"/>
    <Label value="ellipse2" background="blue"/>
  </EllipseLabels>
</View>
"""

PREDICTION_KEYPOINT_CONFIG = """
<View>
  <Image name="image" value="$image"/>
  <KeyPoint name="keypoint" toName="image"/>
</View>
"""

PREDICTION_KEYPOINT_LABELS_CONFIG = """
<View>
  <Image name="image" value="$image"/>
  <KeyPointLabels name="keypointlabels" toName="image">
    <Label value="keypoint1" background="red"/>
    <Label value="keypoint2" background="blue"/>
  </KeyPointLabels>
</View>
"""

PREDICTION_POLYGON_CONFIG = """
<View>
  <Image name="image" value="$image"/>
  <Polygon name="polygon" toName="image"/>
</View>
"""

PREDICTION_POLYGON_LABELS_CONFIG = """
<View>
  <Image name="image" value="$image"/>
  <PolygonLabels name="polygonlabels" toName="image">
    <Label value="polygon1" background="red"/>
    <Label value="polygon2" background="blue"/>
  </PolygonLabels>
</View>
"""

PREDICTION_RECTANGLE_CONFIG = """
<View>
  <Image name="image" value="$image"/>
  <Rectangle name="rectangle" toName="image"/>
</View>
"""

PREDICTION_RECTANGLE_LABELS_CONFIG = """
<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="rectanglelabels" toName="image">
    <Label value="rectangle1" background="red"/>
    <Label value="rectangle2" background="blue"/>
  </RectangleLabels>
</View>
"""

PREDICTION_VIDEO_RECTANGLE_CONFIG = """
<View>
  <Video name="video" value="$video"/>
  <VideoRectangle name="videorectangle" toName="video"/>
</View>
"""

PREDICTION_NUMBER_CONFIG = """
<View>
  <Text name="text" value="$text"/>
  <Number name="number" toName="text" min="0" max="100"/>
</View>
"""

PREDICTION_DATETIME_CONFIG = """
<View>
  <Text name="text" value="$text"/>
  <DateTime name="datetime" toName="text"/>
</View>
"""

PREDICTION_HYPERTEXT_LABELS_CONFIG = """
<View>
  <HyperText name="hypertext" value="$hypertext"/>
  <HyperTextLabels name="hypertextlabels" toName="hypertext">
    <Label value="html1" background="red"/>
    <Label value="html2" background="blue"/>
  </HyperTextLabels>
</View>
"""

PREDICTION_PAIRWISE_CONFIG = """
<View>
  <Text name="text1" value="$text1"/>
  <Text name="text2" value="$text2"/>
  <Pairwise name="pairwise" toName="text1,text2"/>
</View>
"""

PREDICTION_PARAGRAPH_LABELS_CONFIG = """
<View>
  <Paragraphs name="paragraphs" value="$paragraphs"/>
  <ParagraphLabels name="paragraphlabels" toName="paragraphs">
    <Label value="para1" background="red"/>
    <Label value="para2" background="blue"/>
  </ParagraphLabels>
</View>
"""

PREDICTION_RANKER_CONFIG = """
<View>
  <Text name="text" value="$text"/>
  <Ranker name="ranker" toName="text">
    <Choice value="rank1"/>
    <Choice value="rank2"/>
    <Choice value="rank3"/>
  </Ranker>
</View>
"""

PREDICTION_RATING_CONFIG = """
<View>
  <Text name="text" value="$text"/>
  <Rating name="rating" toName="text" maxRating="5"/>
</View>
"""

PREDICTION_RELATIONS_CONFIG = """
<View>
  <Text name="text" value="$text"/>
  <Labels name="labels" toName="text">
    <Label value="label1" background="red"/>
    <Label value="label2" background="blue"/>
  </Labels>
  <Relations name="relations" toName="text"/>
</View>
"""

PREDICTION_TAXONOMY_CONFIG = """
<View>
  <Text name="text" value="$text"/>
  <Taxonomy name="taxonomy" toName="text">
    <Choice value="category1">
      <Choice value="subcategory1"/>
      <Choice value="subcategory2"/>
    </Choice>
    <Choice value="category2">
      <Choice value="subcategory3"/>
    </Choice>
  </Taxonomy>
</View>
"""

PREDICTION_TEXTAREA_CONFIG = """
<View>
  <Text name="text" value="$text"/>
  <TextArea name="textarea" toName="text"/>
</View>
"""

PREDICTION_TIMESERIES_LABELS_CONFIG = """
<View>
  <TimeSeries name="timeseries" value="$timeseries"/>
  <TimeSeriesLabels name="timeserieslabels" toName="timeseries">
    <Label value="ts1" background="red"/>
    <Label value="ts2" background="blue"/>
  </TimeSeriesLabels>
</View>
"""

PREDICTION_COMPLEX_CONFIG = """
<View>
  <Text name="text" value="$text"/>
  <Choices name="choices" toName="text">
    <Choice value="choice1"/>
    <Choice value="choice2"/>
  </Choices>
  <Labels name="labels" toName="text">
    <Label value="label1" background="red"/>
    <Label value="label2" background="blue"/>
  </Labels>
</View>
"""

# Self-referencing tag configs: tags where from_name == to_name
PREDICTION_CHAT_CONFIG = """
<View>
  <Chat name="chat" value="$messages"/>
</View>
"""

PREDICTION_REACTCODE_CONFIG = """
<View>
  <ReactCode style="height: 95vh" name="code" toName="code" outputs="field1, field2"/>
</View>
"""

PREDICTION_REACTCODE_CONFIG_WITHOUT_TO_NAME = """
<View>
  <ReactCode style="height: 95vh" name="code" outputs="field1, field2"/>
</View>
"""
