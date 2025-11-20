# movie/repository.py
import os
import json

from pymongo import MongoClient

from config import USE_MONGO, MONGO_URI, MONGO_DB_NAME

script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "databases", "movies.json")

_client = None
_db = None
_movies_col = None

if USE_MONGO:
    _client = MongoClient(f"{MONGO_URI}")
    _db = _client[MONGO_DB_NAME]
    _movies_col = _db["movies"]


def _load_json_movies():
    if not os.path.exists(json_path):
        return []

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return data.get("movies", [])
    return data


def _write_json_movies(movies):
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"movies": movies}, f, ensure_ascii=False, indent=2)


def get_all_movies():
    if USE_MONGO:
        return list(_movies_col.find({}, {"_id": 0}))
    return _load_json_movies()


def get_movie_by_id(movie_id: str):
    if USE_MONGO:
        return _movies_col.find_one({"id": str(movie_id)}, {"_id": 0})

    for movie in _load_json_movies():
        if str(movie.get("id")) == str(movie_id):
            return movie
    return None


def get_movie_by_title(title: str):
    if USE_MONGO:
        return _movies_col.find_one({"title": title}, {"_id": 0})

    for movie in _load_json_movies():
        if str(movie.get("title")) == str(title):
            return movie
    return None


def add_movie(movie: dict):
    # harmoniser l'id en string comme pour user
    if "id" in movie:
        movie["id"] = str(movie["id"])

    movie_id = movie.get("id")
    if not movie_id:
        # on laisse la route gérer l'erreur si besoin
        return None

    if USE_MONGO:
        if _movies_col.find_one({"id": movie_id}):
            return None
        _movies_col.insert_one(movie)
        return _movies_col.find_one({"id": movie_id}, {"_id": 0})

    movies = _load_json_movies()
    for m in movies:
        if str(m.get("id")) == str(movie_id):
            return None

    movies.append(movie)
    _write_json_movies(movies)
    return movie


def update_movie_rating(movie_id: str, rate: str):
    if USE_MONGO:
        res = _movies_col.update_one(
            {"id": str(movie_id)},
            {"$set": {"rating": rate}},
        )
        if res.matched_count == 0:
            return None
        return _movies_col.find_one({"id": str(movie_id)}, {"_id": 0})

    movies = _load_json_movies()
    updated_movie = None

    for m in movies:
        if str(m.get("id")) == str(movie_id):
            m["rating"] = rate
            updated_movie = m
            break

    if updated_movie is not None:
        _write_json_movies(movies)

    return updated_movie


def delete_movie(movie_id: str):
    if USE_MONGO:
        deleted = _movies_col.find_one({"id": str(movie_id)}, {"_id": 0})
        if not deleted:
            return None
        _movies_col.delete_one({"id": str(movie_id)})
        return deleted

    movies = _load_json_movies()
    deleted_movie = None
    remaining = []

    for m in movies:
        if deleted_movie is None and str(m.get("id")) == str(movie_id):
            deleted_movie = m
        else:
            remaining.append(m)

    if deleted_movie is not None:
        _write_json_movies(remaining)

    return deleted_movie
