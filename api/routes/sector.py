from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload

from api.models.sector import AssetsSector, SectorEntry
from api.schemas.sector import AssetsSectorSchema, SectorEntrySchema
from app import database
from api.request_schemas.sector import SectorQuerySchema, AssetSectorQuerySchema


sector_blueprint = Blueprint("sector", __name__, url_prefix="/sector")

sectorentry_schema = SectorEntrySchema()
assetsector_schema = AssetsSectorSchema()


@sector_blueprint.route("/", methods=["GET"])
def get_sectorentry():
    args = request.args
    methodology = args.get("methodology",type=str)
    
    if methodology:
        args = SectorQuerySchema().validate(args)
        result = SectorEntry.query.filter_by(**args).all()
        result = sectorentry_schema.dump(result,many=True)
        return jsonify(result) , 200
    
    result = SectorEntry.query.all()
    result = sectorentry_schema.dump(result,many=True)
    return jsonify(result) , 200 
   
@sector_blueprint.route("/assets/", methods=["GET"])
def get_assetsector():
    args = request.args

    if args:
        error = AssetSectorQuerySchema().validate(args)
        if error:
            return jsonify({"error":"Bad request","message":error})
        result =  AssetsSector.query.options(joinedload(AssetsSector.sector_entry)).filter_by(**args).all()
        try:
            result_json = assetsector_schema.dump(result, many=True)
        except ValueError:
            result_json = assetsector_schema.dump(result)
        return jsonify(result_json), 200            


    result = AssetsSector.query.options(joinedload(AssetsSector.sector_entry)).all()
    result = assetsector_schema.dump(result, many=True)
    return jsonify(result), 200


@sector_blueprint.route("/assets/", methods=["POST"])
def create_assetsector():
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        return (
            jsonify({"error": "Bad Request", "message": "Content-Type not supported"}),
            400,
        )
    if request.json:
        try:
            teste = assetsector_schema.load(request.json)
            try:
                database.session.add(teste)
                database.session.commit()
            except Exception as exc:
                return (
                    jsonify({"error": "Server Unavailable", "message": "######"}),
                    400,
                )
        except ValidationError as err:
            return jsonify({"error": "Bad Request", "message": err}), 400
    return jsonify(request.json), 200


def a():
    args = request.args
    ticker = args.get("ticker", type=str)
    methodology = args.get("methodology", type=str)

    if not args:
        result = AssetsSector.query.options(joinedload(AssetsSector.sector_entry)).all()
        result = assetsector_schema.dump(result, many=True)
        return jsonify(result), 200

    if ticker:
        result = (
            AssetsSector.query.options(joinedload(AssetsSector.sector_entry))
            .filter_by(ticker=ticker)
            .all()
        )
        try:
            result_json = assetsector_schema.dump(result, many=True)
        except ValueError:
            result_json = assetsector_schema.dump(result)
        return jsonify(result_json), 200

    if methodology:
        result = (
            AssetsSector.query.join(AssetsSector.sector_entry, aliased=True)
            .filter_by(methodology=methodology)
            .all()
        )

        try:
            result_json = assetsector_schema.dump(result, many=True)
        except ValueError:
            result_json = assetsector_schema.dump(result)
        return jsonify(result_json), 200

    return jsonify({"error": "Bad Request", "message": "#####"}), 400
