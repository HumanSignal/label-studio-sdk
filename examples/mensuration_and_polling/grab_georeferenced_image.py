from sentinelhub import (
    SHConfig,
    BBox,
    CRS,
    DataCollection,
    SentinelHubRequest,
    bbox_to_dimensions,
)
from datetime import datetime, timedelta


def to_local_utm_crs(bbox: BBox):
    assert bbox.crs == CRS.WGS84
    lon, lat = bbox.middle

    # Calculate UTM zone number
    utm_zone = int((lon + 180) / 6) + 1

    # Determine hemisphere (northern or southern)
    is_north_hemisphere = lat >= 0

    # https://epsg.io
    epsg_code = f"326{utm_zone:0>2}" if is_north_hemisphere else f"327{utm_zone:0>2}"

    crs = CRS(epsg_code)
    assert crs.is_utm()

    return bbox.transform_bounds(crs)


def download_image(
    bbox: BBox, start_time: datetime, end_time: datetime, config: SHConfig
):
    evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: ["B04", "B03", "B02", "SCL"],  // RGB and Scene Classification
            output: { bands: 3 }
        };
    }
    function evaluatePixel(sample) {
        if (sample.SCL === 3 || sample.SCL === 8 || sample.SCL === 9 || sample.SCL === 10) {
            return [0, 0, 0];  // Exclude cloudy, shadow, and cirrus pixels
        }
        return [sample.B04, sample.B03, sample.B02];  // RGB
    }
    """

    utm_bbox = to_local_utm_crs(bbox)

    request = SentinelHubRequest(
        data_folder="data",
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=(start_time, end_time),
                mosaicking_order="leastCC",
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", "tiff"),
        ],
        bbox=utm_bbox,
        size=bbox_to_dimensions(utm_bbox, resolution=10),
        config=config,
    )

    request.save_data()


if __name__ == "__main__":

    # sign up with a trial account at https://sentinel-hub.com and create an OAuth client
    config = SHConfig()
    config.sh_client_id = "cee4e332-5202-4f6c-b159-f87debf7e733"
    config.sh_client_secret = "w7sAaO3njHFoL3p9CQxxqKZPPkfVVC8f"

    # lon-lat bounding box of the Grand Canyon
    bbox = BBox(bbox=(-112.2, 36.0, -112.0, 36.2), crs=CRS.WGS84)

    # get a cloud-free composite of images from the last 60 days
    start_time = datetime.utcnow() - timedelta(days=60)
    end_time = datetime.utcnow()

    download_image(bbox, start_time, end_time, config)
