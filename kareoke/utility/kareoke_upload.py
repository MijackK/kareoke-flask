from minio import Minio
import os
import secrets
from flask import current_app


def generate_object_id(name):
    object_id = name.rsplit(".", 1)[0].lower() + secrets.token_urlsafe()
    extension = name.rsplit(".", 1)[1].lower()
    return {
        "object_id": f"{object_id}.{extension}".replace(" ", ""),
        "extension": extension,
    }


def generate_file_object(file):
    image_size = os.fstat(file.fileno()).st_size
    info = generate_object_id(file.filename)
    return {
        "object_id": info["object_id"],
        "extension": info["extension"],
        "size": image_size,
        "file": file,
    }


# file is an array of dictionaries, {object_id,size,file}
def upload_files(files):
    client = Minio(
        "localhost:9000",
        secure=False,
        access_key=os.environ["OBJECT_SERVER_USERNAME"],
        secret_key=os.environ["OBJECT_SERVER_PASSWORD"],
    )
    # check if the bucket exists
    bucket = current_app.config["UPLOAD_BUCKET"]
    found = client.bucket_exists(bucket)
    files_added = 0

    if not found:
        client.make_bucket(bucket)

    for file_data in files:
        filename = file_data["object_id"]
        size = file_data["size"]
        image = file_data["file"]

        result = client.put_object(
            bucket_name=bucket,
            object_name=filename,
            data=image,
            length=size,
            content_type=image.content_type,
        )

        print(
            {
                "message": "sucessfully added",
                "name": image.filename,
                "objectID": result.object_name,
                "size": f"{size/1000/1000} mb",
            }
        )
        files_added += 1

    return f"{files_added}/{len(files)} sucessfully stored"


def delete_files(remove_files):
    client = Minio(
        "localhost:9000",
        secure=False,
        access_key=os.environ["OBJECT_SERVER_USERNAME"],
        secret_key=os.environ["OBJECT_SERVER_PASSWORD"],
    )
    for file in remove_files:
        client.remove_object(bucket_name=os.environ["UPLOAD_BUCKET"], object_name=file)
        print(f"{file} succesfully removed")
