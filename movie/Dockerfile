# image plus légère que "python"
FROM python:3.10-slim

# On bosse depuis /app (où il y aura tout le projet)
WORKDIR /app

# Copier les dépendances depuis la racine du projet
# (on va build avec context = .)
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier **tout** le projet dans l'image (config.py compris)
COPY . .

# Aller dans le dossier user pour lancer le service
WORKDIR /app/movie

EXPOSE 3200

# Démarrage du service user
CMD ["python", "movie.py"]