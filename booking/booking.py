from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound
import os

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

script_dir = os.path.dirname(os.path.abspath(__file__))
with open(f'{script_dir}/databases/bookings.json', "r") as jsf:
    bookings = json.load(jsf)["bookings"]


def write(booking):
    with open(f'{script_dir}/databases/bookings.json', 'w') as f:
        full = {}
        full['bookings'] = bookings
        json.dump(full, f)


def auth(req_body, url_userid):
    if not req_body or "user_id" not in req_body:
        return make_response(jsonify({"error": "Authenticaiton failed"}), 400)

    try:
        resp = requests.get(f"http://localhost:3203/users/{req_body['user_id']}")
    except Exception as e:
        return make_response(jsonify({"error": "Users service unavailable", "detail": str(e)}), 503)

    if resp.status_code != 200:
        return make_response(jsonify({"error": "Invalid user_id"}), 401)

    payload = resp.json()
    is_admin = bool(payload.get("is_admin") or payload.get("role") == "admin")

    if not is_admin and str(req_body["user_id"]) != str(url_userid):
        return make_response(jsonify({"error": "Forbidden"}), 403)

    return None  # authorized


@app.route("/booking/<userid>", methods=['GET'])
def get_booking_by_userid(userid):
    req_body = request.get_json()
    is_auth = auth(req_body, userid)
    if is_auth is not None:
        return is_auth

    for booking in bookings:
        if str(booking["userid"]) == userid:
            res = make_response(jsonify(booking), 200)
            return res
    return make_response(jsonify({"error": "User id not found"}), 500)


@app.route("/booking", methods=['POST'])
def add_booking():
    req = request.get_json()
    for booking in bookings:
        if str(booking["userid"]) == str(req["userid"]):
            return make_response(jsonify({"error": "Bookings for this user already exists"}), 500)

    try:
        resp = requests.get(f"http://localhost:3203/users/{req["userid"]}")
        if resp.status_code != 200:
            return make_response(jsonify({"error": f"Invalid user ID: {req["userid"]}"}), 500)
    except Exception as e:
        return make_response(jsonify({"error": "Users service unavailable", "detail": str(e)}), 503)

    try:
        for dates in req["dates"]:
            resp = requests.get(f"http://localhost:3202/schedule/{dates["date"]}")
            if resp.status_code != 200:
                return make_response(jsonify({"error": f"No movies avalaible for this date: {dates["date"]}"}), 500)
            for movie in dates["movies"]:
                if movie not in resp.json().get("movies", []):
                    return make_response(
                        jsonify({"error": f"Movie {movie} not available for this date: {dates['date']}"}), 500)
    except Exception as e:
        return make_response(jsonify({"error": "Schedule service unavailable", "detail": str(e)}), 503)

    bookings.append(req)
    write(bookings)
    return make_response(jsonify({"message": "Booking added"}), 200)


@app.route("/booking/<userid>", methods=['DELETE'])
def delete_schedule(userid):
    req_body = request.get_json()
    is_auth = auth(req_body, userid)
    if is_auth is not None:
        return is_auth

    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            bookings.remove(booking)
            write(bookings)
            return make_response(jsonify(booking), 200)
    return make_response(jsonify({"error": "User id not found"}), 500)


@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
