# Mensuration with Label Studio

![screenshot](data/Screenshot%20from%202024-06-14%2009-18-21.png)

Label georeferenced images in Label Studio, and use the SDK to perform [mensuration](https://pro.arcgis.com/en/pro-app/latest/arcpy/image-analyst/mensuration-class.htm) (measure real-world distances within the image) using the labels produced.

In this example, the [Label Studio SDK](https://labelstud.io/sdk/index.html) is run in a separately running background task that watches for new annotations, calculates the desired distances for each one, and adds the distance to the annotation as a new field.

You will learn:

- How to download and work with satellite imagery
- How to label polygons in Label Studio
- How to compute distances in georeferenced images
- How to use the Label Studio SDK to poll for new annotations and modify task data (this is a toy example - for production use cases, we recommend using Plugins in Label Studio Enterprise for real-time updates to the labeling interface on [annotation events](https://labelstud.io/guide/frontend_reference#Annotation-events).)

> [!WARNING]
> 
> This example predates the Plugins feature. Consider using Plugins for this use case instead of polling using the SDK. 

## Setup data

Any georeferenced raster images can be used. For this demo, two images are used:

### Grand Canyon satellite image

a georeferenced TIFF image of the Grand Canyon and a corresponding PNG image that can be loaded into Label Studio (TIFF is not supported in Label Studio) was generated using the following steps:

1. Sign up at sentinel-hub.com for a trial account for access to [Sentinel-2](https://en.wikipedia.org/wiki/Sentinel-2) satellite images on demand. These have a resolution of 10m GSD (10 meters per pixel).
2. Use the included `grab_georeferenced_image.py` with your credentials to download the image in a [UTM coordinate system](https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system), where each pixel is a fixed area instead of a fixed fraction of longitude and latitude. This makes the image "square" with respect to the ground.
3. Export to PNG:
```bash
convert data/e9b9661bcbd97b67f45364aafd82f9d6/response.tiff data/response.png
```

### Urban drone image

A UAV image of a city block was downloaded from [OpenAerialMap](https://openaerialmap.org/) and cropped to a reasonable size using [QGIS](https://www.qgis.org/en/site/). It has a resolution of 20cm GSD, so it started out as a huge file. Then it was exported to PNG in the same way.

## Load data into Label Studio

Create a new project and upload `data/response.png` and `666dbadcf1cf8e0001fb2f51_cropped.png` to the project.

Add a label config for image segmentation, slightly modified from the default template:

```xml
<View>

  <Header value="Select label and click the image to start"/>
  <Image name="image" value="$image" zoom="true"/>

  <PolygonLabels name="label" toName="image" strokeWidth="3" pointSize="small" opacity="0.9">
    <Label value="label_name" background="red"/>
  </PolygonLabels>
  <Text name="perimeter_m" value="Perimeter in m: $perimeter_m" editable="false" />
  <Text name="area_m^2" value="Area in m^2: $area_m2" editable="false" />
  <Text name="length_m" value="Length in m: $major_axis_m" editable="false" />
  <Text name="width_m" value="Width in m: $minor_axis_m" editable="false" />

</View>
```

Add a cloud storage to host your images. If you're running Label Studio locally, you can set `LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true` to use local file storage.

Upload a JSON manifest describing where your files are. Here's an example for S3:
```json
[
  {
    "data": {
      "image": "s3://my-bucket/path/image1.jpg",
      "perimeter_m": "placeholder",
      "area_m2": "placeholder",
      "major_axis_m": "placeholder",
      "minor_axis_m": "placeholder"
    }
  },
  {
    "data": {
      "image": "s3://my-bucket/path/image2.jpg",
      "perimeter_m": "placeholder",
      "area_m2": "placeholder",
      "major_axis_m": "placeholder",
      "minor_axis_m": "placeholder"
    }
  }
]
```

## Run background task

Edit `poll_for_tasks.py` with your Label Studio URL, API key, and project ID.

You API key can be found in your Label Studio `Account & Settings` page from clicking on your profile picture in the upper right.

Your project ID can be found in the URL of the project page: `<base_url>/projects/<id>`.

Then run it in another window while Label Studio is running:
```bash
pip install -r requirements.txt
python poll_for_tasks.py
```

Refresh the page between starting the background task and creating new annotations to ensure that it started correctly.


## Create or edit a georeferenced polygon annotation


When you draw a polygon on the image and `Update` or `Submit` it, you should see the area and perimeter displayed under the image after refreshing the page.
