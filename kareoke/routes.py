from flask import Blueprint,request
from kareoke.utility.kareoke_upload import upload_files
from kareoke.models import BeatMap,Media
from minio import Minio
from minio.error import S3Error
import os
from app import db



kareoke = Blueprint("/kareoke", __name__, url_prefix='/kareoke')

@kareoke.route("/add_song", methods=['PUT'] )
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
    background = request.files['background']
    filename = audio.filename
    size = os.fstat(audio.fileno()).st_size
    files = request.files.getlist("folder")

    return False
    
 
    
    result = client.put_object(
        bucket_name="kareoke", 
        object_name=filename, #generate unique object name
        data=audio, 
        length=size
    )
    
    return {
        "message":"sucessfully created",
        "id":result.version_id,
        "size":f"{size/1000/1000} mb"
    }

@kareoke.route("/add_map", methods=['PUT'] )
def create_map():
    background = request.files['background']
    song_id = Media.query.get(1).id

    result = upload_files([background])
    #save the background to database
    new_background = Media(
        name =result["objects"][0]["name"], 
        bucket="kareoke", 
        isBackground=True
    )
    db.session.add(new_background)
    db.session.commit()

    #create the beat map

    db.session.add(BeatMap(
        name = request.form['name'], 
        audio = song_id, 
        background = new_background.id,
        song_map = ""
    ))
    db.session.commit()

    return result['message']

@kareoke.route("/get_maps", methods=["GET"])
def get_maps():
    #add pagination later
    get_maps = BeatMap.query.all()
    response = []
    for beat_map in get_maps:
        response.append(
            {
                "name":beat_map.name,
                "id":beat_map.id
            }
        )
    return response



    

      
   
