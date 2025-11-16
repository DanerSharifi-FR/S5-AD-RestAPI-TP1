# schedule/repository.py
import os
import json

from pymongo import MongoClient

from config import USE_MONGO, MONGO_URI, MONGO_DB_NAME

script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "databases", "times.json")

_client = None
_db = None
_schedule_col = None

if USE_MONGO:
    _client = MongoClient(MONGO_URI)
    _db = _client[MONGO_DB_NAME]
    # on a importé les données dans la collection "times"
    _schedule_col = _db["times"]


def _load_json_schedule():
    if not os.path.exists(json_path):
        return []

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return data.get("schedule", [])
    return data


def _write_json_schedule(schedule_list):
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"schedule": schedule_list}, f, ensure_ascii=False, indent=2)


def get_all_schedule():
    if USE_MONGO:
        return list(_schedule_col.find({}, {"_id": 0}))
    return _load_json_schedule()


def get_schedule_by_date(date: str):
    if USE_MONGO:
        return _schedule_col.find_one({"date": str(date)}, {"_id": 0})

    for day in _load_json_schedule():
        if str(day.get("date")) == str(date):
            return day
    return None


def add_schedule_entry(day: dict):
    """
    day = {"date": "...", "movies": [...]}
    """
    date_value = day.get("date")
    if not date_value:
        return None

    if USE_MONGO:
        if _schedule_col.find_one({"date": str(date_value)}):
            return None
        _schedule_col.insert_one(day)
        return _schedule_col.find_one({"date": str(date_value)}, {"_id": 0})

    schedule_list = _load_json_schedule()
    for d in schedule_list:
        if str(d.get("date")) == str(date_value):
            return None

    schedule_list.append(day)
    _write_json_schedule(schedule_list)
    return day


def delete_schedule_by_date(date: str):
    if USE_MONGO:
        deleted = _schedule_col.find_one({"date": str(date)}, {"_id": 0})
        if not deleted:
            return None
        _schedule_col.delete_one({"date": str(date)})
        return deleted

    schedule_list = _load_json_schedule()
    deleted_day = None
    remaining = []

    for d in schedule_list:
        if deleted_day is None and str(d.get("date")) == str(date):
            deleted_day = d
        else:
            remaining.append(d)

    if deleted_day is not None:
        _write_json_schedule(remaining)

    return deleted_day
