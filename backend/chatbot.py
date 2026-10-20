"""
Le "cerveau" du chatbot (Sprint 1) : décide quoi répondre à un message.

Ordre de traitement :
  1. Petites phrases de politesse (bonjour, merci, au revoir)  -> réponse directe
  2. Recherche dans la base de connaissances :
       - score élevé       -> on donne la réponse
       - score moyen       -> on propose les questions les plus proches ("Vouliez-vous dire…")
       - score trop faible -> réponse de secours + contact humain
"""

import re

SEUIL_CONFIANCE = 0.45   # au-dessus : on est assez sûr de la réponse
SEUIL_SUGGESTION = 0.30  # entre les deux : on propose des questions proches

SMALL_TALK = [
    (r"(?i)^\s*(bonjour|salut|hello|coucou|bonsoir|hi|hey)\b[\s!.,]*$",
     "Bonjour ! 👋 Je suis l'assistant virtuel de l'ESIC. Posez-moi vos questions sur les emplois du temps, "
     "les procédures, les services du campus ou le règlement."),
    (r"(?i)^\s*(merci|thanks|thank you|super|parfait|top)\b.*$",
     "Avec plaisir ! 😊 Puis-je vous aider avec autre chose ?"),
    (r"(?i)^\s*(au revoir|bye|à plus|a plus|bonne journée|bonne soirée|ciao)\b.*$",
     "Au revoir et bonne continuation ! 👋"),
]

REPONSE_SECOURS = (
    "Désolé, je n'ai pas trouvé de réponse à votre question. 🤔\n\n"
    "Vous pouvez reformuler, ou contacter directement le service scolarité :\n"
    "📧 scolarite@esic.fr | ☎️ 01.53.90.15.20 (Lun-Ven 9h-12h / 14h-17h)"
)


class Chatbot:
    def __init__(self, base):
        self.base = base

    def repondre(self, message):
        """Renvoie un dictionnaire décrivant la réponse."""
        for motif, reponse in SMALL_TALK:
            if re.match(motif, message):
                return {"reponse": reponse, "statut": "small_talk", "suggestions": []}

        resultats = self.base.rechercher(message)
        meilleure, score = resultats[0]

        if score >= SEUIL_CONFIANCE:
            return {
                "reponse": meilleure["reponse"],
                "statut": "repondu",
                "source_id": meilleure["id"],
                "categorie": meilleure["categorie"],
                "score": round(score, 3),
                "suggestions": [],
            }

        if score >= SEUIL_SUGGESTION:
            return {
                "reponse": "Je ne suis pas sûr d'avoir compris. Vouliez-vous dire :",
                "statut": "clarification",
                "categorie": meilleure["categorie"],
                "score": round(score, 3),
                "suggestions": [e.get("libelle", e["question"]) for e, _ in resultats],
            }

        return {
            "reponse": REPONSE_SECOURS,
            "statut": "non_compris",
            "score": round(score, 3),
            "suggestions": self.base.questions_frequentes(3),
        }
