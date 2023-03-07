from minio import Minio
from minio.error import S3Error


def upload_file():
    client = Minio(
        "localhost:9000",
        secure=False,
        access_key="minioadmin",
        secret_key="minioadmin",
    )
    #check if the bucket exists
    found = client.bucket_exists("kareoke")

    if not found:
        client.make_bucket("kareoke")
    else:
        print("Bucket 'kareoke' already exists")
    