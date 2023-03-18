from flask import Blueprint, request, session, abort
from kareoke.utility.kareoke_upload import upload_files
from kareoke.models import BeatMap, Media, Bucket
from minio import Minio
from minio.error import S3Error
import os
from app import db



kareoke = Blueprint("/kareoke", __name__, url_prefix='/kareoke')

@kareoke.route("/add_song", methods=['PUT'] )
def add_song():
    song = background = request.files['song']
    result = upload_files([song])
    new_song = Media(
        name =result["objects"][0]["name"], 
        bucket="kareoke", 
        isBackground=False
    )
    db.session.add(new_song)
    db.session.commit()

    return result


@kareoke.route("/get_songs", methods=['GET'] )
def get_songa():
    get_songs = Media.query.filter(Media.isBackground==False)
    songs = []
    for song in get_songs:
        songs.append(
            {
                "id":song.id,
                "name":song.name
            }
        )
    return songs


@kareoke.route("/add_map", methods=['PUT'] )
def create_map():
    #add user need to be verified decorator here
    background = request.files['background']
    song = Media.query.get(request.form['song'])
    if not song:
        return{
            "success":False,
            "message":"Could not find song"
        }
    

    result = upload_files([background])
    #save the background to database
    new_background = Media(
        name =result["objects"][0]["name"],
        bucket = "kareoke", 
        isBackground = True
    )
    db.session.add(new_background)
    db.session.commit()

    #create the beat map

    db.session.add(BeatMap(
        name = request.form["map-name"], 
        audio = song.id, 
        background = new_background.id,
        song_map = ""
    ))
    db.session.commit()
    print(result['message'])

    return {
        'success':True,
        'message':f"beatmap {request.form['map-name']} added"
    }

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

@kareoke.route("/get_map", methods=["GET"])
def get_map():
    map_id = request.args.get('mapID')
   
    #update this query to use aggregator function to put all the
    #media in an array
    get_map = BeatMap.query.filter(BeatMap.id == map_id).first()
    if not get_map:
        abort(404)
       
    audio = Media.query.get(beat_map.audio)
    background = Media.query.get(beat_map.background)
      
    response = {
        "name":beat_map.name,
        "id":beat_map.id,
        "audio":f"kareoke/{audio.name}",
        "background":f"kareoke/{background.name}"
    }
        
    return response


@kareoke.route("/get_user_maps", methods=["GET"])
def get_user_maps():
    #add pagination later
    user_id = 1
    #update this query to use aggregator function to put all the
    #media in an array
    get_maps = BeatMap.query.filter(BeatMap.user == user_id)
    response = []
    for beat_map in get_maps:
        audio = Media.query.get(beat_map.audio)
        background = Media.query.get(beat_map.background)
      
        response.append(
            {
                "name":beat_map.name,
                "id":beat_map.id,
                "audio":f"kareoke/{audio.name}",
                "background":f"kareoke/{background.name}"
            }
        )
    return response


    

      
   
