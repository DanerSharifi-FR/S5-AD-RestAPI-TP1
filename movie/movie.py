from flask import Flask, request, jsonify, make_response
from werkzeug.exceptions import NotFound
import os
import sys
from flask_cors import CORS

# allow imports from project root (config, etc.)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from repository import (
    get_all_movies,
    get_movie_by_id,
    get_movie_by_title,
    add_movie,
    update_movie_rating,
    delete_movie,
)
from config import MOVIE_PORT, HOST

app = Flask(__name__)

# Autoriser Swagger UI (localhost:8080) à appeler notre API
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})

@app.route("/", methods=["GET"])
def home():
    return "<h1 style='color:blue'>Welcome to the Movie service!</h1>"

@app.route("/movies/<movieid>", methods=["GET"])
def get_movie_byid(movieid):
    movie = get_movie_by_id(movieid)
    if movie is None:
        return make_response(jsonify({"error": "Movie ID not found"}), 500)
    return make_response(jsonify(movie), 200)


@app.route("/json", methods=["GET"])
def get_json():
    movies = get_all_movies()
    return make_response(jsonify(movies), 200)


@app.route("/moviesbytitle", methods=["GET"])
def get_movie_by_title_route():
    if not request.args or "title" not in request.args:
        return make_response(jsonify({"error": "missing 'title' query param"}), 400)

    title = request.args["title"]
    movie = get_movie_by_title(title)

    if not movie:
        return make_response(jsonify({"error": "movie title not found"}), 500)

    return make_response(jsonify(movie), 200)


# Create
@app.route("/movies/<movieid>", methods=["POST"])
def add_movie_route(movieid):
    req = request.get_json() or {}

    # forcer cohérence body/path
    if str(req.get("id")) != str(movieid):
        req["id"] = str(movieid)

    created = add_movie(req)
    if created is None:
        return make_response(jsonify({"error": "movie ID already exists"}), 500)

    return make_response(jsonify({"message": "movie added"}), 200)


# Update
@app.route("/movies/<movieid>/<rate>", methods=["PUT"])
def update_movie_rating_route(movieid, rate):
    updated = update_movie_rating(movieid, rate)
    if updated is None:
        return make_response(jsonify({"error": "movie ID not found"}), 500)

    return make_response(jsonify(updated), 200)


# Delete
@app.route("/movies/<movieid>", methods=["DELETE"])
def del_movie(movieid):
    deleted = delete_movie(movieid)
    if deleted is None:
        return make_response(jsonify({"error": "movie ID not found"}), 500)

    return make_response(jsonify(deleted), 200)


if __name__ == "__main__":
    print("Server running in port %s" % (MOVIE_PORT))
    app.run(host=HOST, port=MOVIE_PORT)
