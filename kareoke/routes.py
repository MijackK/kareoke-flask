from flask import Blueprint, request, session, abort, current_app
from kareoke.utility.kareoke_upload import (
    upload_files,
    delete_files,
    generate_file_object,
    generate_url,
)
from kareoke.models import BeatMap, HighScore, Media
from authentication.models import User
import json
from sqlalchemy import and_, func, or_, case
from authentication.decorator import login_required, require_admin, require_verify
from app import db, limiter


kareoke = Blueprint("kareoke", __name__, url_prefix="/kareoke")


@kareoke.route("/add_map", methods=["POST"])
@limiter.limit("5 per day")
@require_verify
def create_map():
    drafts_amount = BeatMap.query.filter(
        BeatMap.status != "published", BeatMap.user == session["user_id"]
    ).count()
    if drafts_amount >= current_app.config["DRAFT_LIMIT"]:
        abort(403, "post limit reached")

    background = request.files["background"]
    audio = request.files["audio"]

    new_map = BeatMap(
        name=request.form["map-name"], beatMap="[]", user=session["user_id"]
    )
    db.session.add(new_map)
    db.session.flush()

    background_info = generate_file_object(background)
    audio_info = generate_file_object(audio)
    print(background_info["size"] + audio_info["size"])

    if (
        background_info["size"] + audio_info["size"]
        > current_app.config["MAX_MAP_SIZE"]
    ):
        abort(
            403,
            f'Media size can not be larger than {current_app.config["MAX_MAP_SIZE"] / 1000000}MB',
        )
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
    try:
        result = upload_files([background_info, audio_info])
        print(result)
        beatMap = {
            "id": new_map.id,
            "name": new_map.name,
            "beatMap": new_map.beatMap,
            "background": generate_url(new_background.objectID),
            "audio": generate_url(new_audio.objectID),
            "dateUpdated": new_map.date_updated,
            "status": new_map.status,
        }

        return {
            "message": f"beatmap {request.form['map-name']} added",
            "map": beatMap,
        }
    except Exception as e:
        print(e)
        abort(
            500,
            "some of you're files might not have been uploaded, realod the page to check that everything is alright",
        )


@kareoke.route("/get_published", methods=["GET"])
def get_published():
    karaoke = request.headers.get("Cookie")
    return f"<h1 style='color:blue'>Hello There! request cookies are {karaoke} and {session} </h1>"

    page = int(request.args.get("page"))
    search_keys = (
        request.args.get("search").split(",")
        if request.args.get("searchKey") != ""
        else []
    )

    words_subquery = (
        db.session.query(BeatMap)
        .with_entities(
            BeatMap.id.label("post"),
            func.unnest(func.string_to_array(BeatMap.name, " ")).label("word"),
        )
        .filter(
            BeatMap.status == "published",
            or_(*[BeatMap.name.ilike(f"%{key}%") for key in search_keys]),
        )
        .subquery()
    )

    get_maps = (
        db.session.query(BeatMap)
        .select_from(BeatMap)
        .join(words_subquery, BeatMap.id == words_subquery.c.post)
        .with_entities(
            BeatMap.id.label("id"),
            BeatMap.name.label("name"),
        )
        .group_by(BeatMap.id, BeatMap.name)
        .order_by(
            func.count(
                case(
                    *[
                        (words_subquery.c.word.ilike(f"%{key}%"), 1)
                        for key in search_keys
                    ],
                    else_=None,
                )
            ).desc(),
            BeatMap.date_created.desc(),
        )
        .paginate(page=page, per_page=current_app.config["PAGE_LIMIT"], error_out=False)
        .items
    )
    response = []
    for beat_map in get_maps:
        response.append({"name": beat_map.name, "id": beat_map.id})
    return response


@kareoke.route("/get_map", methods=["GET"])
def get_map():
    map_id = request.args.get("mapID")
    user = User.query.get(session.get("user_id"))
    is_admin = False
    if user:
        is_admin = user.admin

    # media in an array
    map_data = (
        db.session.query(BeatMap, Media, User, HighScore)
        .select_from(BeatMap)
        .join(Media)
        .join(User)
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
        .filter(
            or_(
                BeatMap.user == session.get("user_id"),
                BeatMap.status == "published",
                is_admin,
            )
        )
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
        "audio": generate_url(audio),
        "background": generate_url(background),
        "dateUpdated": beat_map.date_updated,
        "author": author,
        "highscore": highscore if highscore else 0,
        "status": beat_map.status,
    }

    return response


@kareoke.route("/get_user_maps", methods=["GET"])
@login_required
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
                "background": generate_url(background),
                "audio": generate_url(audio),
                "dateUpdated": beat_map.date_updated,
                "status": beat_map.status,
            }
        )

    return response


@kareoke.route("/save_map", methods=["PUT"])
@login_required
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
    if beat_map.status != "draft":
        abort(403, "Can only edit draft maps.")

    setattr(beat_map, post_data["column"], value)

    db.session.add(beat_map)
    db.session.commit()
    return f"beatMap '{beat_map.name}' updated"


@kareoke.route("/change_media", methods=["PUT"])
@limiter.limit("5 per day")
@login_required
def change_audio():
    map_id = request.form["mapID"]
    type = request.form["type"]
    new_media = request.files["media"]
    media_data = (
        db.session.query(Media, BeatMap)
        .select_from(Media)
        .join(BeatMap)
        .with_entities(Media, BeatMap.status.label("status"))
        .filter(BeatMap.user == session["user_id"])
        .filter(Media.beatMap == map_id)
    )

    #
    media = None
    status = None
    size = 0

    for value in media_data:
        if value.Media.type == type:
            media = value.Media
            status = value.status
        else:
            size += value.Media.size

    if media is None:
        abort(404)

    if status != "draft":
        abort(403, "Can only edit draft maps.")

    media_info = generate_file_object(new_media)
    if size + media_info["size"] > current_app.config["MAX_MAP_SIZE"]:
        abort(
            403,
            f"file too large, must be smaller than or equal to {(current_app.config['MAX_MAP_SIZE']-size)/1000000}MB",
        )

    # add media
    result = upload_files([media_info])
    print(result)
    # delete media
    delete_files([media.objectID])

    media.objectID = media_info["object_id"]
    media.size = media_info["size"]
    db.session.commit()

    return generate_url(media.objectID)


@kareoke.route("/delete_map", methods=["DELETE"])
@login_required
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


@kareoke.route("/publish_request", methods=["POST"])
@login_required
def publish_request():
    post_data = request.get_json()
    beat_map_id = post_data["beatMapID"]
    status_dict = {"published": "draft", "draft": "pending", "pending": "draft"}

    map = BeatMap.query.filter(
        BeatMap.id == beat_map_id,
        BeatMap.user == session["user_id"],
    ).first()
    if map is None:
        abort(403)

    map.status = status_dict[map.status]
    db.session.commit()
    return map.status


@kareoke.route("/get_maps", methods=["GET"])
@require_admin
def get_maps():
    requests = (
        db.session.query(BeatMap, User)
        .select_from(BeatMap)
        .join(User)
        .with_entities(
            BeatMap.id.label("id"),
            BeatMap.name.label("name"),
            BeatMap.status.label("status"),
            User.username.label("author"),
            User.id.label("userID"),
            User.username.label("username"),
        )
    )
    requests_list = []
    for map in requests:
        requests_list.append(
            {
                "id": map.id,
                "name": map.name,
                "author": map.author,
                "userID": map.userID,
                "userName": map.username,
                "status": map.status,
            }
        )
    return requests_list


@kareoke.route("/publish_map", methods=["POST"])
@require_admin
def publish_map():
    post_data = request.get_json()
    map = BeatMap.query.get(post_data["beatMapID"])
    map.status = post_data["resolution"]
    # maybe send email to user, or implement notifications
    db.session.commit()
    return "map published"


@kareoke.route("/delete_map_admin", methods=["DELETE"])
@require_admin
def delete_map_admin():
    post_data = request.get_json()

    # get the beat map
    target = (
        db.session.query(BeatMap, Media)
        .select_from(BeatMap)
        .join(Media)
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
