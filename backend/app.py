"""
Serveur web Flask : expose l'API du chatbot.

Routes (= "adresses" de l'API) :
  GET  /api/health       -> vérifier que le serveur tourne
  GET  /api/suggestions  -> questions fréquentes à afficher dans le chat (US-005)
  POST /api/chat         -> envoyer une question, recevoir une réponse (US-001)
  GET  /api/logs         -> voir les derniers échanges enregistrés (US-011)
"""

import os
import time

from flask import Flask, jsonify, request
from flask_cors import CORS

import database
from chatbot import Chatbot
from knowledge_base import BaseConnaissances
from security import LimiteurDebit, detecter_injection, valider_message

app = Flask(__name__)
# CORS autorise le frontend (http://localhost:5173) à appeler ce serveur (http://localhost:5001)
CORS(app)
app.json.ensure_ascii = False  # renvoie les accents tels quels (é au lieu de \u00e9)

# Chargés UNE seule fois au démarrage (et pas à chaque question) pour aller vite
base = BaseConnaissances(os.environ.get("DATA_DIR", "../data/clean"))
chatbot = Chatbot(base)
limiteur = LimiteurDebit(max_requetes=10, fenetre_secondes=60)


@app.get("/api/health")
def health():
    return jsonify({"statut": "ok", "entrees": len(base.entrees)})


@app.get("/api/suggestions")
def suggestions():
    return jsonify({"suggestions": base.questions_frequentes()})


@app.post("/api/chat")
def chat():
    debut = time.perf_counter()
    donnees = request.get_json(silent=True) or {}
    session_id = str(donnees.get("session_id", ""))[:64] or "anonyme"

    # 1. Limitation du débit (US-013) : code HTTP 429 = "Too Many Requests"
    if not limiteur.autoriser(session_id):
        return jsonify({"erreur": "Trop de questions ! Attendez une minute avant de réessayer. ⏳"}), 429

    # 2. Validation de l'entrée : code HTTP 400 = "Bad Request"
    message, erreur = valider_message(donnees.get("message"))
    if erreur:
        return jsonify({"erreur": erreur}), 400

    # 3. Filtrage des tentatives d'injection (US-012)
    attaque = detecter_injection(message)
    if attaque:
        reponse = "⛔ Votre message contient des éléments non autorisés et n'a pas été traité."
        database.enregistrer_echange(session_id, message, reponse, "bloque", categorie=attaque)
        return jsonify({"reponse": reponse, "statut": "bloque", "suggestions": []})

    # 4. Recherche de la réponse
    resultat = chatbot.repondre(message)
    temps_ms = round((time.perf_counter() - debut) * 1000)
    resultat["temps_reponse_ms"] = temps_ms

    # 5. Enregistrement de l'échange (US-011)
    database.enregistrer_echange(
        session_id, message, resultat["reponse"], resultat["statut"],
        source_id=resultat.get("source_id"), categorie=resultat.get("categorie"),
        score=resultat.get("score"), temps_reponse_ms=temps_ms,
    )
    return jsonify(resultat)


@app.get("/api/logs")
def logs():
    limite = min(request.args.get("limite", 50, type=int), 500)
    return jsonify(database.derniers_echanges(limite))
