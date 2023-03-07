from flask import Blueprint,request
from kareoke.utility import  kareoke_upload
from minio import Minio
from minio.error import S3Error
import os

kareoke = Blueprint("/kareoke", __name__, url_prefix='/kareoke')

@kareoke.route("/create", methods=['PUT'] )
def create_song():
    client = Minio(
        "localhost:9000",
        secure=False,
        access_key="minioadmin",
        secret_key="minioadmin",
    )
    #check if the bucket exists
    found = client.bucket_exists("kareoke")
    audio = request.files['audio']
    filename = audio.filename
    size = os.fstat(audio.fileno()).st_size
   
    
 
    if not found:
        client.make_bucket("kareoke")
    else:
        print("Bucket 'kareoke' already exists")
    
    result = client.put_object(
        bucket_name="kareoke", 
        object_name=filename, 
        data=audio, 
        length=size
    )
    
    return {
        "message":"sucessfully created",
        "id":result.etag,
        "size":size/1000
    }