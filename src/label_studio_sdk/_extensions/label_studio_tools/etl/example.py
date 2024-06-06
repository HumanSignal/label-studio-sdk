from label_studio_sdk._extensions.label_studio_tools.etl.registry import (
    transform,
    call_dataloader,
)


@transform.datarecords("read_base64_from_blob")
def gcs_blob_to_base64(
    key: str,
    bucket_name: str,
    google_project_id: str = None,
):
    print(key, bucket_name)


if __name__ == "__main__":
    call_dataloader("gcs_blob_reader", key=12, bucket_name=34)
