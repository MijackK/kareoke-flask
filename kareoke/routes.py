from flask import Blueprint, request, session, abort
from kareoke.utility.kareoke_upload import (
    upload_files,
    delete_files,
    generate_file_object,
)
from kareoke.models import BeatMap, HighScore, Media
from authentication.models import User
import traceback
import json
from sqlalchemy import and_, func
from authentication.decorator import login_required
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
        background_info = generate_file_object(background)
        audio_info = generate_file_object(audio)
        # save the background to database
        new_background = Media(
            beatMap=new_map.id,
            objectID=background_info["object_id"],
            size=background_info["size"],
            type="background",
        )
        new_audio = Media(
            beatMap=new_map.id,
            objectID=audio_info["object_id"],
            size=audio_info["size"],
            type="audio",
        )
        db.session.add(new_background)
        db.session.add(new_audio)
        db.session.commit()
        result = upload_files([background_info, audio_info])
        print(result)
        beatMap = {
            "id": new_map.id,
            "name": new_map.name,
            "beatMap": new_map.beatMap,
            "background": f"kareoke/{new_background.objectID}",
            "audio": f"kareoke/{new_audio.objectID}",
            "dateUpdated": new_map.date_updated,
        }

        return {
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
    map_data = (
        db.session.query(BeatMap, Media, User, HighScore)
        .select_from(BeatMap)
        .join(Media)
        .outerjoin(
            HighScore,
            and_(
                HighScore.beatMap == BeatMap.id,
                HighScore.user == session.get("user_id"),
            ),
        )
        .with_entities(
            BeatMap,
            User.username.label("username"),
            HighScore.score.label("score"),
            func.array_agg(
                func.json_build_object("type", Media.type, "objectID", Media.objectID)
            ).label("media"),
        )
        .filter(BeatMap.id == map_id)
        .group_by(BeatMap, User.username, HighScore.score)
        .first()
    )
    if not map_data:
        abort(404, "Map does not exists")

    beat_map = map_data.BeatMap
    author = map_data.username
    highscore = map_data.score
    audio = [value["objectID"] for value in map_data.media if value["type"] == "audio"][
        0
    ]
    background = [
        value["objectID"] for value in map_data.media if value["type"] == "background"
    ][0]

    response = {
        "name": beat_map.name,
        "id": beat_map.id,
        "beatMap": beat_map.beatMap,
        "audio": f"kareoke/{audio}",
        "background": f"kareoke/{background}",
        "dateUpdated": beat_map.date_updated,
        "author": author,
        "highscore": highscore if highscore else 0,
    }

    return response


@kareoke.route("/get_user_maps", methods=["GET"])
def get_user_maps():
    get_maps = (
        db.session.query(BeatMap, Media)
        .select_from(BeatMap)
        .join(Media)
        .with_entities(
            BeatMap,
            func.array_agg(
                func.json_build_object("type", Media.type, "objectID", Media.objectID)
            ),
        )
        .filter(BeatMap.user == session["user_id"])
        .group_by(
            BeatMap,
        )
    )
    response = []
    for beat_map, media_data in get_maps:
        audio = [value["objectID"] for value in media_data if value["type"] == "audio"][
            0
        ]
        background = [
            value["objectID"] for value in media_data if value["type"] == "background"
        ][0]
        response.append(
            {
                "id": beat_map.id,
                "name": beat_map.name,
                "beatMap": beat_map.beatMap,
                "background": f"kareoke/{background}",
                "audio": f"kareoke/{audio}",
                "dateUpdated": beat_map.date_updated,
            }
        )

    return response


@kareoke.route("/save_map", methods=["PUT"])
def save_map():
    editable_columns = ["name", "beatMap"]
    post_data = request.get_json()
    value = post_data["value"]

    if post_data["column"] not in editable_columns:
        abort(500)

    if type(value) is list:
        value = json.dumps(value)

    beat_map = (
        BeatMap.query.filter(BeatMap.id == post_data["id"])
        .filter(BeatMap.user == session["user_id"])
        .first()
    )
    if beat_map is None:
        abort(404, "Could not update Beat Map")

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


@kareoke.route("/delete_map", methods=["DELETE"])
def delete_map():
    post_data = request.get_json()

    # get the beat map
    target = (
        db.session.query(BeatMap, Media)
        .select_from(BeatMap)
        .join(Media)
        .filter(BeatMap.user == session["user_id"])
        .filter(BeatMap.id == post_data["id"])
        .with_entities(
            BeatMap,
            func.array_agg(Media.objectID).label("media"),
        )
        .group_by(BeatMap)
        .first()
    )

    if target is None:
        abort(404, "Map does not exist in database")
    db.session.delete(target.BeatMap)
    delete_files(remove_files=target.media)
    db.session.commit()

    return "map deleted"


@kareoke.route("/highscore", methods=["PUT"])
@login_required
def add_highscore():
    post_data = request.get_json()
    beat_map_id = post_data["beatMapID"]
    score = post_data["score"]

    get_highscore = HighScore.query.filter(
        HighScore.beatMap == beat_map_id, HighScore.user == session["user_id"]
    ).first()
    # update highscore
    if get_highscore and get_highscore.score < score:
        get_highscore.score = score
        db.session.add(get_highscore)

    # create new highscore
    if get_highscore is None:
        db.session.add(
            HighScore(beatMap=beat_map_id, score=score, user=session["user_id"])
        )

    db.session.commit()

    return "highscore added"
