from flask import Flask, request, jsonify, make_response
import requests
from werkzeug.exceptions import NotFound
import os
import sys
from flask_cors import CORS

# allow imports from project root (config, etc.)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from repository import (
    get_all_bookings,
    get_booking_by_userid,
    add_booking,
    delete_booking_by_userid,
)
from config import USER_SERVICE_URL, USER_PORT, SCHEDULE_SERVICE_URL, SCHEDULE_PORT, BOOKING_PORT, HOST

app = Flask(__name__)

# Autoriser Swagger UI (localhost:8080) à appeler notre API
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})

def auth(req_body, url_userid):
    """
    Vérifie que :
      - le corps contient user_id
      - le user_id existe dans le service users
      - soit l'utilisateur est admin, soit il ne tente pas de lire/supprimer la réservation d'un autre.
    """
    if not req_body or "user_id" not in req_body:
        return make_response(jsonify({"error": "Authenticaiton failed"}), 400)

    user_id = req_body["user_id"]

    try:
        resp = requests.get(f"{USER_SERVICE_URL}:{USER_PORT}/users/{user_id}")
    except Exception as e:
        return make_response(
            jsonify({"error": "Users service unavailable", "detail": str(e)}),
            503,
        )

    if resp.status_code != 200:
        return make_response(jsonify({"error": "Invalid user_id"}), 401)

    payload = resp.json()
    is_admin = bool(payload.get("is_admin") or payload.get("role") == "admin")

    if not is_admin and str(user_id) != str(url_userid):
        return make_response(jsonify({"error": "Forbidden"}), 403)

    return None  # authorized


@app.route("/booking/<userid>", methods=["GET"])
def get_booking_by_userid_route(userid):
    """
    Récupère la réservation d'un utilisateur.
    Nécessite un JSON body avec "user_id" pour l'auth (user lui-même ou admin).
    """
    req_body = request.get_json()
    is_auth = auth(req_body, userid)
    if is_auth is not None:
        return is_auth

    booking = get_booking_by_userid(userid)
    if booking is None:
        return make_response(jsonify({"error": "User id not found"}), 500)

    return make_response(jsonify(booking), 200)


@app.route("/booking", methods=["GET"])
def get_all_bookings_route():
    """Retourne toutes les réservations (utile pour debug)."""
    bookings_list = get_all_bookings()
    return make_response(jsonify(bookings_list), 200)


@app.route("/booking", methods=["POST"])
def add_booking_route():
    """
    Crée une réservation :
      {
        "userid": "...",
        "dates": [
          { "date": "2025-11-20", "movies": ["id1", "id2"] },
          ...
        ]
      }
    """
    req = request.get_json() or {}

    userid = req.get("userid")
    dates = req.get("dates")

    if not userid or not isinstance(dates, list):
        return make_response(
            jsonify({"error": "Missing or invalid 'userid' or 'dates' field"}),
            400,
        )

    # Vérifier qu'il n'y a pas déjà une réservation pour cet utilisateur
    existing = get_booking_by_userid(userid)
    if existing is not None:
        return make_response(
            jsonify({"error": "Bookings for this user already exists"}),
            500,
        )

    # Vérifier l'utilisateur via le service user
    try:
        resp = requests.get(f"{USER_SERVICE_URL}/users/{userid}")
        if resp.status_code != 200:
            return make_response(
                jsonify({"error": f"Invalid user ID: {userid}"}),
                500,
            )
    except Exception as e:
        return make_response(
            jsonify({"error": "Users service unavailable", "detail": str(e)}),
            503,
        )

    # Vérifier les dates et les films via le service schedule
    try:
        for date_entry in dates:
            date_value = date_entry.get("date")
            movies_for_date = date_entry.get("movies", [])

            if not date_value or not isinstance(movies_for_date, list):
                return make_response(
                    jsonify({"error": "Invalid 'date' or 'movies' structure"}),
                    400,
                )

            # Check que la date existe dans schedule
            resp = requests.get(f"{SCHEDULE_SERVICE_URL}:{SCHEDULE_PORT}/schedule/{date_value}")
            if resp.status_code != 200:
                return make_response(
                    jsonify(
                        {"error": f"No movies avalaible for this date: {date_value}"}
                    ),
                    500,
                )

            available_schedule = resp.json()
            available_movies = available_schedule.get("movies", [])

            # Vérifier que chaque film demandé est dispo ce jour-là
            for movie in movies_for_date:
                if movie not in available_movies:
                    return make_response(
                        jsonify(
                            {
                                "error": (
                                    f"Movie {movie} not available for this date: "
                                    f"{date_value}"
                                )
                            }
                        ),
                        500,
                    )

    except Exception as e:
        return make_response(
            jsonify({"error": "Schedule service unavailable", "detail": str(e)}),
            503,
        )

    # Si tout est OK -> on persiste via le repository
    new_booking = {
        "userid": str(userid),
        "dates": dates,
    }

    created = add_booking(new_booking)
    if created is None:
        # En théorie déjà géré plus haut, mais on garde un filet
        return make_response(
            jsonify({"error": "Bookings for this user already exists"}),
            500,
        )

    return make_response(jsonify({"message": "Booking added"}), 200)


@app.route("/booking/<userid>", methods=["DELETE"])
def delete_booking_route(userid):
    """
    Supprime la réservation d'un utilisateur.
    Nécessite un JSON body avec "user_id" pour l'auth (user lui-même ou admin).
    """
    req_body = request.get_json()
    is_auth = auth(req_body, userid)
    if is_auth is not None:
        return is_auth

    deleted = delete_booking_by_userid(userid)
    if deleted is None:
        return make_response(jsonify({"error": "User id not found"}), 500)

    return make_response(jsonify(deleted), 200)


@app.route("/", methods=["GET"])
def home():
    return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"


if __name__ == "__main__":
    print("Server running in port %s" % (BOOKING_PORT))
    app.run(host=HOST, port=BOOKING_PORT)
