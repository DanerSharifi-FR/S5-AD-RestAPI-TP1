import requests
from flask import Flask, request, jsonify, make_response
from werkzeug.exceptions import NotFound
import os
import sys

# allow imports from project root (config, etc.)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from repository import (
    get_all_schedule,
    get_schedule_by_date,
    add_schedule_entry,
    delete_schedule_by_date,
)
from config import MOVIE_SERVICE_URL

app = Flask(__name__)

PORT = 3202
HOST = "0.0.0.0"


@app.route("/", methods=["GET"])
def home():
    return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"


@app.route("/schedule/<date>", methods=["GET"])
def get_schedule_bydate(date):
    day = get_schedule_by_date(date)
    if day is None:
        return make_response(jsonify({"error": "Date not found"}), 500)
    return make_response(jsonify(day), 200)


@app.route("/schedule", methods=["GET"])
def get_schedule_json():
    schedule_list = get_all_schedule()
    return make_response(jsonify(schedule_list), 200)


@app.route("/schedule", methods=["POST"])
def add_schedule():
    req = request.get_json() or {}

    date_value = req.get("date")
    movies_ids = req.get("movies")

    if not date_value or not isinstance(movies_ids, list):
        return make_response(
            jsonify({"error": "Missing or invalid 'date' or 'movies' field"}),
            400,
        )

    # validation des films via le service movie
    try:
        for movie_id in movies_ids:
            resp = requests.get(f"{MOVIE_SERVICE_URL}/movies/{movie_id}")
            if resp.status_code != 200:
                return make_response(
                    jsonify({"error": f"Invalid movie ID: {movie_id}"}),
                    500,
                )
    except Exception as e:
        return make_response(
            jsonify({"error": "Movies service unavailable", "detail": str(e)}),
            503,
        )

    new_day = {
        "date": date_value,
        "movies": movies_ids,
    }

    created = add_schedule_entry(new_day)
    if created is None:
        return make_response(jsonify({"error": "Date already exists"}), 500)

    return make_response(jsonify({"message": "Date added"}), 200)


@app.route("/schedule/<date>", methods=["DELETE"])
def delete_schedule(date):
    deleted = delete_schedule_by_date(date)
    if deleted is None:
        return make_response(jsonify({"error": "Date not found"}), 500)
    return make_response(jsonify(deleted), 200)


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
