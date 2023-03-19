from minio import Minio
from minio.error import S3Error
import os
import secrets


def upload_files(files):
    client = Minio(
        "localhost:9000",
        secure=False,
        access_key=os.environ['OBJECT_SERVER_USERNAME'],
        secret_key=os.environ['OBJECT_SERVER_PASSWORD'],
    )
    #check if the bucket exists
    found = client.bucket_exists("kareoke")
    new_objects = []
    files_added = 0
    

    if not found:
        abort(500)

    for media in files:
        filename = media.filename.rsplit('.', 1)[0].lower() + secrets.token_urlsafe()
        extension = media.filename.rsplit('.', 1)[1].lower()

        #check if extension is allowed
        size = os.fstat(media.fileno()).st_size
        #check that file type isnt to large.
        result = client.put_object(
            bucket_name = "kareoke", 
            object_name = f"{filename}.{extension}", 
            data = media, 
            length = size,
            content_type = media.content_type
        )

        print({
            "message":"sucessfully added",
            "name":result.object_name,
            "size":f"{size/1000/1000} mb"
        })
        new_objects.append({
            "name":result.object_name,
            "size":size
        })
        files_added += 1
    
    return {
        "message":f"{files_added}/{len(files)} sucessfully stored",
        "objects":new_objects

    }
      


