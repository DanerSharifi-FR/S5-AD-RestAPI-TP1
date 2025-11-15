# config.py
import os

# Si python-dotenv est installé, on charge automatiquement les variables
# depuis un fichier `.env` situé à la racine du projet (même dossier que ce fichier).
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Si python-dotenv n'est pas installé, on ignore simplement.
    # Les variables devront venir de l'environnement (bash, Docker, etc.).
    pass

# Toggle Mongo (0 = JSON, 1 = Mongo)
USE_MONGO = os.getenv("USE_MONGO", "0") == "1"

# Paramètres Mongo
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "cinema_rest")

# URLs des services (en dehors de Docker => localhost, en Docker => host = nom du service)
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:3203")
SCHEDULE_SERVICE_URL = os.getenv("SCHEDULE_SERVICE_URL", "http://localhost:3202")
MOVIE_SERVICE_URL = os.getenv("MOVIE_SERVICE_URL", "http://localhost:3200")
BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", "http://localhost:3201")