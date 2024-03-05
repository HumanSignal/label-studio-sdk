import os
import boto3
import logging

from botocore.exceptions import ClientError

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Deployment:
    def __init__(self):
        self.b = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        self.s3 = self.b.resource("s3")

    def upload_file(self, import_file):
        name = os.path.basename(import_file)
        logger.info(f"Copy {import_file} => s3://labelstud.io/sdk/{name}")
        try:
            self.s3.meta.client.upload_file(
                import_file,
                "labelstud.io",
                "sdk/" + name,
                ExtraArgs={"ContentType": "text/html", "ACL": "public-read"},
            )
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def upload_dir(self, root_dir):
        logger.info("Copy " + root_dir)
        for path in os.listdir(root_dir):
            if os.path.isdir(path):
                continue

            if path.endswith(".html"):
                self.upload_file(os.path.join(root_dir, path))

    def run(self):
        logger.info("\n\n\n===>  Deployment is running")
        self.upload_dir("html/label_studio_sdk")
        logger.info("\n\n\n===> Deployment is finished")


if __name__ == "__main__":
    d = Deployment()
    d.run()
