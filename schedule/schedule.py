import requests
from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'

with open('{}/databases/times.json'.format("."), "r") as jsf:
    schedule = json.load(jsf)["schedule"]


def write(schedule):
    with open('{}/databases/times.json'.format("."), 'w') as f:
        full = {}
        full['schedule'] = schedule
        json.dump(full, f)


@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"


'''
Schedule format:
{
  "schedule": [
    {
      "date":"20151130",
      "movies":[
        "720d006c-3a57-4b6a-b18f-9b713b073f3c",
        "a8034f44-aee4-44cf-b32c-74cf452aaaae",
        "39ab85e5-5e8e-4dc5-afea-65dc368bd7ab"
      ]
    },
    ...
    ]
}

this endpoint returns the list of movies for a given date
we will code the CRD operations
'''


@app.route("/schedule/<date>", methods=['GET'])
def get_schedule_bydate(date):
    for day in schedule:
        if str(day["date"]) == str(date):
            res = make_response(jsonify(day), 200)
            return res
    return make_response(jsonify({"error": "Date not found"}), 500)


@app.route("/schedule", methods=['POST'])
def add_schedule():
    req = request.get_json()

    for day in schedule:
        if str(day["date"]) == str(req["date"]):
            return make_response(jsonify({"error": "Date already exists"}), 500)

    try:
        for movie_id in req["movies"]:
            resp = requests.get(f"http://localhost:3200/movies/{movie_id}")
            if resp.status_code != 200:
                return make_response(jsonify({"error": f"Invalid movie ID: {movie_id}"}), 500)
    except Exception as e:
        return make_response(jsonify({"error": "Movies service unavailable", "detail": str(e)}), 503)

    new_day = {
        "date": req["date"],
        "movies": req["movies"]
    }
    schedule.append(new_day)
    write(schedule)
    return make_response(jsonify({"message": "Date added"}), 200)

@app.route("/schedule/<date>", methods=['DELETE'])
def delete_schedule(date):
    for day in schedule:
        if str(day["date"]) == str(date):
            schedule.remove(day)
            write(schedule)
            return make_response(jsonify({"message": "Date deleted"}), 200)
    return make_response(jsonify({"error": "Date not found"}), 500)


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
