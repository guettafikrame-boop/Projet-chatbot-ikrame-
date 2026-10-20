"""
Sécurité de base (Epic 3) :
  - validation des entrées (longueur, caractères invisibles)
  - détection des tentatives d'injection (prompt, SQL, XSS, commandes)  -> US-012
  - limitation du débit : 10 questions / minute / utilisateur            -> US-013
"""

import re
import time
from collections import defaultdict, deque

LONGUEUR_MAX = 500

# Chaque motif est une expression régulière ; (?i) = insensible à la casse
MOTIFS_INJECTION = {
    "injection_prompt": [
        r"(?i)ignore[sz]?\s+(all\s+|toutes?\s+)?(les\s+|the\s+)?(previous\s+|pr[ée]c[ée]dentes?\s+)?(instructions|consignes|r[èe]gles)",
        r"(?i)(oublie|forget)\s+(tout|everything|tes\s+instructions)",
        r"(?i)(system\s+prompt|prompt\s+syst[èe]me)",
        r"(?i)(tu\s+es\s+maintenant|you\s+are\s+now|act\s+as|fais\s+comme\s+si\s+tu\s+[ée]tais)",
    ],
    "injection_sql": [
        r"(?i)\b(drop|delete|truncate|alter)\s+table\b",
        r"(?i)\bunion\s+(all\s+)?select\b",
        r"(?i)'\s*or\s+'?\d+'?\s*=\s*'?\d+",
        r";\s*--",
    ],
    "xss": [
        r"(?i)<\s*(script|iframe|img|svg|object|embed)\b",
        r"(?i)javascript\s*:",
        r"(?i)\bon(error|load|click|mouseover)\s*=",
    ],
    "injection_commande": [
        r"(?i)\brm\s+-rf\b",
        r"\$\(.*\)",
        r"(?i)\b(cat|wget|curl)\s+(/etc/|https?://)",
    ],
}


def valider_message(message):
    """Renvoie (message_nettoyé, erreur). erreur vaut None si tout va bien."""
    if not isinstance(message, str):
        return None, "Le message doit être du texte."
    # Supprime les caractères de contrôle invisibles (sauf retour à la ligne)
    message = "".join(c for c in message if c == "\n" or c.isprintable()).strip()
    if not message:
        return None, "Le message est vide."
    if len(message) > LONGUEUR_MAX:
        return None, f"Le message est trop long ({LONGUEUR_MAX} caractères maximum)."
    return message, None


def detecter_injection(message):
    """Renvoie le type d'attaque détecté, ou None si le message semble sain."""
    for type_attaque, motifs in MOTIFS_INJECTION.items():
        if any(re.search(motif, message) for motif in motifs):
            return type_attaque
    return None


class LimiteurDebit:
    """Fenêtre glissante : on garde l'heure des dernières requêtes de chaque utilisateur."""

    def __init__(self, max_requetes=10, fenetre_secondes=60):
        self.max_requetes = max_requetes
        self.fenetre = fenetre_secondes
        self.historique = defaultdict(deque)  # utilisateur -> heures de ses requêtes

    def autoriser(self, utilisateur):
        maintenant = time.time()
        requetes = self.historique[utilisateur]
        # On oublie les requêtes plus vieilles que la fenêtre (60 s)
        while requetes and requetes[0] < maintenant - self.fenetre:
            requetes.popleft()
        if len(requetes) >= self.max_requetes:
            return False
        requetes.append(maintenant)
        return True
