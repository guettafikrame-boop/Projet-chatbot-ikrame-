"""
Accès à la base PostgreSQL : enregistrement des échanges (US-011) et lecture des logs.
"""

import os

import psycopg
from psycopg.rows import dict_row

# L'adresse de la base est donnée par une variable d'environnement (définie dans docker-compose.yml).
# On ne met jamais un mot de passe "en dur" dans le code.
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://assistant:assistant_dev@localhost:5432/assistant")


def connexion():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def enregistrer_echange(session_id, question, reponse, statut, source_id=None,
                        categorie=None, score=None, temps_reponse_ms=None):
    """Insère une ligne dans la table conversations.

    Les %s sont des "paramètres" : psycopg les remplit lui-même de façon sûre.
    C'est ce qui protège contre l'injection SQL (on ne colle JAMAIS le texte
    de l'utilisateur directement dans la requête).
    """
    try:
        with connexion() as conn:
            conn.execute(
                """INSERT INTO conversations
                   (session_id, question, reponse, statut, source_id, categorie, score, temps_reponse_ms)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (session_id, question, reponse, statut, source_id, categorie, score, temps_reponse_ms),
            )
    except psycopg.Error as erreur:
        # Si la base est indisponible, le chatbot continue de répondre : on signale juste l'erreur
        print(f"[DB] Impossible d'enregistrer l'échange : {erreur}")


def derniers_echanges(limite=50):
    with connexion() as conn:
        return conn.execute(
            "SELECT * FROM conversations ORDER BY created_at DESC LIMIT %s", (limite,)
        ).fetchall()
