import datetime

from flask import jsonify, request
from api.routes.middleoffice import middleoffice_blueprint
from api.models.eventlog import EventLog
from api.request_schemas.dateargs import PeriodSchema, DateSchema
from api.schemas.eventlog import EventLogSchema
import json

eventlog_schema = EventLogSchema()


# TODO : CURRENT / ALL BEHAVIOUR



def get_current_log():
    eventlogs = []
    with open("api/jobs/eventslog.json") as file:
        for line in file:
            eventlogs.append(json.loads(line))
    return eventlogs


def get_eventlog_period(start_date, end_date):
    """

    Get event log between period

    Parameters
    ----------
    start_date : str
        "%Y-%m-%d" format
    end_date : str
        "%Y-%m-%d" format

    """
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")  # type: ignore (Already marshmallow validated)
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")  # type: ignore (Already marshmallow validated)
    start_date_start = start_date.replace(hour=0, minute=0, second=0)
    end_date_end = end_date.replace(hour=23, minute=59, second=59)
    result = EventLog.query.filter(
        EventLog.asctime.between(start_date_start, end_date_end)
    ).all()
    result = eventlog_schema.dump(result, many=True)
    return result


@middleoffice_blueprint.route("/event-logs/", methods=["GET"])
def get_eventlog_date():

    args = request.args
    asctime = args.get("date", type=str)
    start_date = args.get("start_date", type=str)
    end_date = args.get("end_date", type=str)

    if asctime:
        errors = DateSchema().validate(args)
        if errors:
            return jsonify({"error": "Bad Request", "message": errors}), 400

        asctime = datetime.datetime.strptime(asctime, "%Y-%m-%d")
        asctime_start = asctime.replace(hour=0, minute=0, second=0)
        asctime_end = asctime.replace(hour=23, minute=59, second=59)
        result = EventLog.query.filter(
            EventLog.asctime.between(asctime_start, asctime_end)
        ).all()
        result = eventlog_schema.dump(result, many=True)
        return jsonify(result), 200

    if end_date or start_date:
        errors = PeriodSchema().validate(args)
        if errors:
            return jsonify({"error": "Bad Request", "message": errors}), 400

        result = get_eventlog_period(start_date, end_date)
        return jsonify(result), 200

    result = get_current_log()
    return jsonify(result), 200
