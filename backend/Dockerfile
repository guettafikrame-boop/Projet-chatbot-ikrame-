# Image de départ : Python 3.12 en version "slim" (allégée)
FROM python:3.12-slim

# Dossier de travail à l'intérieur du conteneur
WORKDIR /app

# On installe d'abord les dépendances (étape mise en cache par Docker tant que
# requirements.txt ne change pas -> les rebuilds sont beaucoup plus rapides)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Puis on copie le code
COPY . .

EXPOSE 5000

# Serveur de développement Flask (--debug = rechargement automatique quand le code change)
CMD ["flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "5000", "--debug"]
