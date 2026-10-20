-- Script exécuté automatiquement par PostgreSQL au PREMIER démarrage du conteneur.
-- Il crée la table qui enregistre chaque échange avec le chatbot (US-011 : logging).

CREATE TABLE IF NOT EXISTS conversations (
    id               SERIAL PRIMARY KEY,              -- numéro unique, auto-incrémenté
    session_id       VARCHAR(64)  NOT NULL,           -- identifiant ANONYME de la conversation (RGPD)
    question         TEXT         NOT NULL,           -- la question posée
    reponse          TEXT,                            -- la réponse donnée par le bot
    source_id        VARCHAR(32),                     -- ex : "EDT001" (FAQ) ou "PROC002" (procédure)
    categorie        VARCHAR(64),                     -- ex : "emploi_temps"
    score            REAL,                            -- confiance de la recherche (0 à 1)
    statut           VARCHAR(20)  NOT NULL,           -- repondu | clarification | non_compris | bloque | small_talk
    temps_reponse_ms INTEGER,                         -- durée de traitement en millisecondes
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()  -- horodatage (timestamp)
);

-- Un index accélère les recherches par date (utile pour le dashboard)
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations (created_at);
