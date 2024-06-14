# Mensuration with Label Studio

![screenshot](data/Screenshot%20from%202024-06-14%2009-18-21.png)

Label georeferenced images in Label Studio, and use the SDK to perform [mensuration](https://pro.arcgis.com/en/pro-app/latest/arcpy/image-analyst/mensuration-class.htm) (measure real-world distances within the image) using the labels produced.

In this example, the [Label Studio SDK](https://labelstud.io/sdk/index.html) is run in a separately running background task that watches for new annotations, calculates the desired distances for each one, and adds the distance to the annotation as a new field.

You will learn:

- How to download and work with satellite imagery
- How to label polygons in Label Studio
- How to compute distances in georeferenced images
- How to use the Label Studio SDK to poll for new annotations and modify task data (this is a toy example - for production use cases, we recommend using Custom Scripts in Label Studio Enterprise for real-time updates to the labeling interface on [annotation events](https://labelstud.io/guide/frontend_reference#Annotation-events).)


## Setup data

Any georeferenced raster can be used. For this demo, a georeferenced TIFF image of the Grand Canyon and a corresponding PNG image that can be loaded into Label Studio (TIFF is not supported in Label Studio) was generated using the following steps:

1. Sign up at sentinel-hub.com for a trial account for access to [Sentinel-2](https://en.wikipedia.org/wiki/Sentinel-2) satellite images on demand. These have a resolution of 10 GSD (10 meters per pixel).
2. Use the included `grab_georeferenced_image.py` with your credentials to download the image in a [UTM coordinate system](https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system), where each pixel is a fixed area instead of a fixed fraction of longitude and latitude. This makes the image "square" with respect to the ground.
3. Export to PNG:
```bash
convert data/e9b9661bcbd97b67f45364aafd82f9d6/response.tiff data/e9b9661bcbd97b67f45364aafd82f9d6/response.png
```

## Load data into Label Studio

Create a new project and upload `data/e9b9661bcbd97b67f45364aafd82f9d6/response.png` to the project.

Add a label config for image segmentation, slightly modified from the default template:

```xml
<View>

  <Header value="Select label and click the image to start"/>
  <Image name="image" value="$image" zoom="true"/>

  <PolygonLabels name="label" toName="image"
                 strokeWidth="3" pointSize="small"
                 opacity="0.9">
    <Label value="label_name" background="red"/>
  </PolygonLabels>
  <Text name="perimeter_km" value="Perimeter in km: $label_perimeter" editable="false" />
  <Text name="area_km^2" value="Area in km^2: $label_area" editable="false" />

</View>
```

Note: you must upload all your files before setting the label config, to support the workaround where `Text` fields are populated by the SDK when an annotation is updated.


## Run background task

Edit `poll_for_tasks.py` with your Label Studio URL, API key, and project ID.

You API key can be found in your Label Studio `Account & Settings` page from clicking on your profile picture in the upper right.

Your project ID can be found in the URL of the project page: `<base_url>/projects/<id>`.

Then run it in another window while Label Studio is running:
```bash
python poll_for_tasks.py
```


## Create or edit a georeferenced polygon annotation


When you draw a polygon on the image and `Update` or `Submit` it, you should see the area and perimeter displayed under the image after refreshing the page.
