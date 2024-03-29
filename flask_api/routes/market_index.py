from flask import Blueprint, jsonify, request

from flask_api.models.market_index import MarketIndex
from flask_api.request_schemas.dateargs import DateSchema, PeriodSchema
from flask_api.schemas.market_index import MarketIndexSchema
from flask_api.app import database

marketindex_blueprint = Blueprint("MarketIndex", __name__, url_prefix="/marketindex")




@marketindex_blueprint.route("/", methods=["GET"])
def get_marketindex():
    """
    Returns all values associated with all Market Indexes. May be filtered down by date or period.

    ---
    parameters:
      - name: date
        in: query
        type: string
        required: False
        format: 'YYYY-mm-dd'
        description:
            This parameter is incompatible with `start_date` and `end_date`.


      - name: start_date
        in: query
        type: string
        required: False
        format: 'YYYY-mm-dd'
        description:
            The start_date for the period of which the values will be filtered. Must be used together with `end_date`.
            This parameter is incompatible with `date`.

      - name: end_date
        in: query
        type: string
        required: False
        format: 'YYYY-mm-dd'
        description:
            The end_date for the period of which the values will be filtered. Must be used together with `start_date`.
            This parameter is incompatible with `date`.
      
    responses:
        '200':
          description: OK
          schema:
            type: array
            items:
                $ref: '#/definitions/MarketIndex'

        '400':
          description: Bad Request.

    """
    args = request.args
    date = args.get("date", type=str)
    start_date = args.get("start_date", type=str)
    end_date = args.get("end_date", type=str)

    if date:
        error = DateSchema().validate(args)
        if error:
            return jsonify({"error": "Bad request", "message": error}), 400
        result = database.session.query(MarketIndex).filter_by(**args).all()
        result = MarketIndexSchema().dump(result, many=True)
        return jsonify(result), 200

    if start_date or end_date:
        error = PeriodSchema().validate(args)
        if error:
            return jsonify({"error": "Bad request", "message": error}), 400
        result = database.session.query(MarketIndex).filter(
            MarketIndex.date.between(start_date, end_date)
        ).all()

        result = MarketIndexSchema().dump(result, many=True)
        return jsonify(result),200

    result = database.session.query(MarketIndex).all()
    result = MarketIndexSchema().dump(result, many=True)

    return jsonify(result), 200


@marketindex_blueprint.route("/<string:index>/", methods=["GET"])
def get_marketindex_id(index: str):

    """
    Returns all values associated with a Index. May be filtered down by date or period.
    ---

    parameters:
      - name: index
        in: path
        type: string
        required: False

      - name: date
        in: query
        type: string
        required: False
        format:  'YYYY-mm-dd'
        description:
            The date of the values to filter by.
            This parameter is incompatible with `start_date` and `end_date`.

      - name: start_date
        in: query
        type: string
        required: False
        format: 'YYYY-mm-dd'
        description:
            The start_date for the period of which the values will be filtered. Must be used together with `end_date`.
            This parameter is incompatible with `date`.

      - name: end_date
        in: query
        type: string
        required: False
        format: 'YYYY-mm-dd'
        description:
            The end_date for the period of which the values will be filtered. Must be used together with `start_date`.
            This parameter is incompatible with `date`.

    responses:
        '200':
          description: OK
          schema:
            type: array
            items:
                $ref: '#/definitions/MarketIndex'
              
        '400':
          description: Bad Request.

        '404':
          description: Bad Request. field `index` must be string
    """
    args = request.args
    date = args.get("date", type=str)
    start_date = args.get("start_date", type=str)
    end_date = args.get("end_date", type=str)

    if date:
        errors = DateSchema().validate(args)
        if errors:
            return jsonify({"error": "Bad request", "message": errors}), 400

        result = database.session.query(MarketIndex).filter_by(**args, index=index).one_or_none()
        result = MarketIndexSchema().dump(result)
        return jsonify(result), 200

    if start_date or end_date:
        errors = PeriodSchema().validate(args)
        if errors:
            return jsonify({"error": "Bad request", "message": errors}), 400
        result = (
            database.session.query(MarketIndex).filter(MarketIndex.date.between(start_date, end_date))
            .filter_by(index=index)
            .all()
        )
        result = MarketIndexSchema().dump(result, many=True)
        return jsonify(result), 200

    result = database.session.query(MarketIndex).filter_by(index=index).all()
    result = MarketIndexSchema().dump(result, many=True)
    return jsonify(result), 200
