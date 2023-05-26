from flask import Blueprint, request, session, abort
from kareoke.utility.kareoke_upload import upload_files
from kareoke.models import BeatMap, Audio, Background
import traceback
import json

from app import db


kareoke = Blueprint("kareoke", __name__, url_prefix="/kareoke")


@kareoke.route("/add_map", methods=["POST"])
def create_map():
    # add user need to be verified decorator here
    background = request.files["background"]
    audio = request.files["audio"]

    new_map = BeatMap(
        name=request.form["map-name"], beatMap="[]", user=session["user_id"]
    )
    db.session.add(new_map)
    db.session.flush()
    try:
        result = upload_files([background, audio])
        background_info = result["objects"][0]
        audio_info = result["objects"][1]
        # save the background to database
        new_background = Background(
            name=background_info["name"],
            beatMap=new_map.id,
            objectID=background_info["objectID"],
            size=background_info["size"],
        )
        new_audio = Audio(
            name=audio_info["name"],
            beatMap=new_map.id,
            objectID=audio_info["objectID"],
            size=audio_info["size"],
        )
        db.session.add(new_background)
        db.session.add(new_audio)
        db.session.commit()

        print(result["message"])
        beatMap = {
            "id": new_map.id,
            "name": new_map.name,
            "beatMap": new_map.beatMap,
            "background": f"kareoke/{new_background.objectID}",
            "audio": f"kareoke/{new_audio.objectID}",
            "dateUpdated": new_map.date_updated,
        }

        return {
            "success": True,
            "message": f"beatmap {request.form['map-name']} added",
            "map": beatMap,
        }
    except:
        db.session.rollback()
        traceback.print_exc()
        return {
            "success": False,
            "message": f"could not add {request.form['map-name']}",
        }


@kareoke.route("/get_maps", methods=["GET"])
def get_maps():
    # add pagination later
    get_maps = BeatMap.query.all()
    response = []
    for beat_map in get_maps:
        response.append({"name": beat_map.name, "id": beat_map.id})
    return response


@kareoke.route("/get_map", methods=["GET"])
def get_map():
    map_id = request.args.get("mapID")

    # update this query to use aggregator function to put all the
    # media in an array
    get_map = (
        db.session.query(BeatMap, Audio, Background)
        .select_from(BeatMap)
        .join(Audio)
        .join(Background)
        .filter(BeatMap.id == map_id)
        .first()
    )
    if not get_map:
        abort(404)
    beat_map = get_map.BeatMap
    audio = get_map.Audio
    background = get_map.Background

    response = {
        "name": beat_map.name,
        "id": beat_map.id,
        "beatMap": beat_map.beatMap,
        "audio": f"kareoke/{audio.objectID}",
        "background": f"kareoke/{background.objectID}",
        "dateUpdated": beat_map.date_updated,
    }

    return response


@kareoke.route("/get_user_maps", methods=["GET"])
def get_user_maps():
    # update this query to use aggregator function to put all the
    # media in an array
    get_maps = (
        db.session.query(BeatMap, Audio, Background)
        .select_from(BeatMap)
        .join(Audio)
        .join(Background)
        .filter(BeatMap.user == session["user_id"])
    )
    response = []
    for beat_map, audio, background in get_maps:
        response.append(
            {
                "id": beat_map.id,
                "name": beat_map.name,
                "beatMap": beat_map.beatMap,
                "background": f"kareoke/{background.objectID}",
                "audio": f"kareoke/{audio.objectID}",
                "dateUpdated": beat_map.date_updated,
            }
        )

    return response


@kareoke.route("/save_map", methods=["PUT"])
def save_map():
    post_data = request.get_json()
    value = post_data["value"]
    if type(value) is list:
        value = json.dumps(value)

    beat_map = (
        BeatMap.query.filter(BeatMap.id == post_data["id"])
        .filter(BeatMap.user == session["user_id"])
        .first()
    )
    if beat_map is None:
        abort(404)

    setattr(beat_map, post_data["column"], value)

    db.session.add(beat_map)
    db.session.commit()
    return f"beatMap '{beat_map.name}' updated"


@kareoke.route("/change_audio", methods=["PUT"])
def change_audio():
    return "audio changed"


@kareoke.route("/change_background", methods=["PUT"])
def change_background():
    return "background changed"
