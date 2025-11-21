# README – S5-AD-RestAPI-TP1 (REST)

---

<p style="text-align: center">
  <a href="https://www.daner-sharifi.com">
    <img src="https://img.shields.io/badge/Daner%20SHARIFI-FIL A1-blue?style=for-the-badge" alt="Daner SHARIFI">
  </a>
  <a href="mailto:bastien.bouvet@imt-atlantique.net">
    <img src="https://img.shields.io/badge/Bastien%20BOUVET-FIL A1-blueviolet?style=for-the-badge" alt="Bastien BOUVET">
  </a>
</p>

<p style="text-align: center">
  <img src="https://img.shields.io/badge/Python-3.10+-informational?style=flat-square" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Flask-REST-success?style=flat-square" alt="Flask REST" />
  <img src="https://img.shields.io/badge/MongoDB-option-darkgreen?style=flat-square" alt="MongoDB option" />
  <img src="https://img.shields.io/badge/Docker-Microservices-blue?style=flat-square" alt="Docker Microservices" />
  <img src="https://img.shields.io/badge/OpenAPI-Documentation-orange?style=flat-square" alt="OpenAPI Documentation" />
</p>


---

## 1. Installation du projet

### 1.1. Récupérer le code

```bash
git clone https://github.com/DanerSharifi-FR/S5-AD-RestAPI-TP1.git
cd S5-AD-RestAPI-TP1
```

### 1.2. Créer l’environnement Python

Prérequis : **Python 3.10+**, `pip`, `virtualenv` (ou `python -m venv`).

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

Les services Flask sont dans les dossiers :

* `user/user.py`
* `movie/movie.py`
* `schedule/schedule.py`
* `booking/booking.py`

---

## 2. Configuration (.env et Docker)

Le projet utilise un **fichier `.env` à la racine** (chargé par `config.py`) pour les exécutions **hors Docker**, et des variables d’environnement injectées par **docker-compose** pour les exécutions **dans Docker**.

### 2.1. Exemple de `.env` (hors Docker)

À la racine de `S5-AD-RestAPI-TP1` :

```env
# Choix JSON vs Mongo
USE_MONGO=0                # 0 = JSON, 1 = Mongo

# Mongo hors Docker
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=cinema_rest
MONGO_PORT=27017

# Ports des services Flask
USER_PORT=3203
MOVIE_PORT=3200
SCHEDULE_PORT=3202
BOOKING_PORT=3201

# Host Flask
HOST=0.0.0.0

# URLs des services (hors Docker)
USER_SERVICE_URL=http://localhost:3203
MOVIE_SERVICE_URL=http://localhost:3200
SCHEDULE_SERVICE_URL=http://localhost:3202
BOOKING_SERVICE_URL=http://localhost:3201

# Mongo dans Docker (utilisé par docker-compose)
MONGO_URI_DOCKER=mongodb://mongo-rest:27017
```

### 2.2. Env Docker (docker-compose)

Dans `docker-compose.yml`, les services reçoivent :

* `USE_MONGO` (même valeur que dans `.env`)
* `MONGO_URI=${MONGO_URI_DOCKER}`
* `MONGO_DB_NAME=${MONGO_DB_NAME}`

Les services qui appellent d’autres services (booking, schedule) reçoivent aussi des URLs adaptées au réseau Docker (par ex. `http://movie-rest:3200`, `http://user-rest:3203`, etc.).

**Idée :**

* Hors Docker → URLs en `http://localhost:port`
* Dans Docker → URLs en `http://<nom-service>:port`

---

## 3. Documentation API REST

### 3.1. Service User (port 3203)

| Méthode | URL                      | Description                               |
| ------: | ------------------------ | ----------------------------------------- |
|     GET | `/`                      | Message de bienvenue                      |
|     GET | `/users/<userid>`        | Récupérer un utilisateur par id           |
|    POST | `/users/<userid>`        | Créer un utilisateur avec cet id          |
|  DELETE | `/users/<userid>`        | Supprimer un utilisateur                  |
|     PUT | `/users/<userid>/<last>` | Mettre à jour `last_active`               |
|     GET | `/usersbyname?name=...`  | Récupérer un utilisateur par nom          |
|     GET | `/json`                  | Récupérer la liste brute des utilisateurs |

Les données viennent de `user/databases/users.json` ou de la collection Mongo `users` selon `USE_MONGO`.

### 3.2. Service Movie (port 3200)

| Méthode | URL                        | Description                        |
| ------: | -------------------------- | ---------------------------------- |
|     GET | `/`                        | Message de bienvenue               |
|     GET | `/movies/<movieid>`        | Récupérer un film par id           |
|    POST | `/movies/<movieid>`        | Créer un film                      |
|  DELETE | `/movies/<movieid>`        | Supprimer un film                  |
|     PUT | `/movies/<movieid>/<rate>` | Mettre à jour la note (`rating`)   |
|     GET | `/moviesbytitle?title=...` | Récupérer un film par titre        |
|     GET | `/json`                    | Récupérer la liste brute des films |

### 3.3. Service Schedule (port 3202)

| Méthode | URL             | Description                                         |
| ------: | --------------- | --------------------------------------------------- |
|     GET | `/`             | Message de bienvenue                                |
|     GET | `/schedule/<d>` | Récupérer le planning pour la date `d`              |
|    POST | `/schedule`     | Créer un planning (date + films), vérifie les films |
|  DELETE | `/schedule/<d>` | Supprimer le planning d’une date                    |

Le POST vérifie les films via `MOVIE_SERVICE_URL`.

### 3.4. Service Booking (port 3201)

| Méthode | URL              | Description                                     |
| ------: | ---------------- | ----------------------------------------------- |
|     GET | `/`              | Message de bienvenue                            |
|     GET | `/booking/<uid>` | Récupérer la réservation de l’utilisateur `uid` |
|    POST | `/booking`       | Créer une réservation pour un utilisateur       |
|  DELETE | `/booking/<uid>` | Supprimer la réservation de l’utilisateur `uid` |

* Auth simple par user-id (user doit exister).
* Vérifie la cohérence des dates/films via le service Schedule.

---

## 4. Comment lancer les 4 cas

On note :

* **JSON** = fichiers `*/databases/*.json`
* **Mongo** = base `cinema_rest` sur un MongoDB (local ou Docker)

### Cas 1 – App non conteneurisée + JSON

1. Dans `.env` :

   ```env
   USE_MONGO=0
   ```

2. Ne pas lancer de Mongo.

3. Lancer chaque service dans un terminal différent :

   ```bash
   source .venv/bin/activate

   python user/user.py
   python movie/movie.py
   python schedule/schedule.py
   python booking/booking.py
   ```

---

### Cas 2 – App non conteneurisée + Mongo conteneurisée

1. Dans `.env` :

   ```env
   USE_MONGO=1
   ```

2. Lancer Mongo en Docker :

   ```bash
   docker compose up mongo
   ```

3. **Seeder** Mongo à partir des JSON (script fourni au root) :

   ```bash
   source .venv/bin/activate
   python import_json_into_mongo.py
   ```

4. Lancer les services Flask comme au cas 1 :

   ```bash
   python user/user.py
   python movie/movie.py
   python schedule/schedule.py
   python booking/booking.py
   ```

---

### Cas 3 – App conteneurisée + JSON

1. Dans `.env` :

   ```env
   USE_MONGO=0
   ```

2. Lancer docker-compose :

   ```bash
   docker compose up user movie schedule booking
   ```

3. Les services utilisent les volumes `./*/databases:/app/*/databases` pour lire/écrire les JSON.
   Le container Mongo peut tourner mais **n’est pas utilisé** (USE_MONGO=0).

---

### Cas 4 – App conteneurisée + Mongo conteneurisée

1. Dans `.env` :

   ```env
   USE_MONGO=1
   ```

2. Démarrer Mongo (ex. via compose) :

   ```bash
   docker compose up mongo
   ```

3. **Seeder** Mongo à partir des JSON (script fourni au root) :

   ```bash
   source .venv/bin/activate
   python import_json_into_mongo.py
   ```

4. Lancer tous les services en Docker :

   ```bash
   docker compose up --build
   ```

---