"""
Base de connaissances : charge la FAQ et les procédures, puis retrouve la
réponse la plus proche d'une question grâce à TF-IDF + similarité cosinus.

Idée générale :
  1. On transforme chaque question connue en un VECTEUR de nombres (TF-IDF).
  2. On transforme la question de l'utilisateur en vecteur de la même façon.
  3. On compare les vecteurs (similarité cosinus) : plus le score est proche
     de 1, plus les questions se ressemblent.
"""

import json
import unicodedata
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Correspondance entre la catégorie d'une procédure et une catégorie de la FAQ
CATEGORIE_PROCEDURE = {
    "Administrative": "procedures_admin",
    "Académique": "procedures_admin",
    "Stage & Alternance": "procedures_admin",
    "Services Campus": "services_campus",
    "Vie Étudiante": "reglement_vie_etudiante",
    "International": "orientation_formation",
    "Sécurité": "reglement_vie_etudiante",
}


def normaliser(texte):
    """Minuscules + suppression des accents : 'Où est la Bibliothèque' -> 'ou est la bibliotheque'."""
    texte = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in texte if unicodedata.category(c) != "Mn")


def formater_procedure(proc):
    """Transforme une fiche procédure (JSON) en un texte lisible pour l'utilisateur."""
    lignes = [f"**{proc['titre']}**", proc.get("description", ""), ""]
    if proc.get("documents_necessaires"):
        lignes.append("**Documents nécessaires :**")
        lignes += [f"- {doc}" for doc in proc["documents_necessaires"]]
        lignes.append("")
    lignes.append("**Étapes :**")
    lignes += [f"{e['numero']}. {e['titre']} : {e['description']}" for e in proc.get("etapes", [])]
    if proc.get("delais"):
        lignes += ["", f"**Délais :** {proc['delais']}"]
    if proc.get("contacts"):
        c = proc["contacts"][0]
        lignes.append(f"**Contact :** {c.get('service', '')} – {c.get('email', '')} – {c.get('telephone', '')}")
    return "\n".join(lignes)


class BaseConnaissances:
    def __init__(self, dossier_donnees):
        dossier = Path(dossier_donnees)
        self.entrees = []      # chaque entrée = une question connue + sa réponse
        self.categories = {}   # id de catégorie -> nom lisible
        self._charger_faq(dossier / "faq.json")
        self._charger_procedures(dossier / "procedures_esic.json")
        self._charger_annuaire(dossier / "annuaire_contacts.json")

        # Le texte "indexé" d'une entrée = sa question + ses mots-clés (tags)
        textes = [normaliser(e["question"] + " " + " ".join(e["tags"])) for e in self.entrees]

        # analyzer="char_wb" : on découpe en petits morceaux de 3 à 5 lettres.
        # Avantage : "biblio", "bibliotheque" et "bibliothèque" se ressemblent,
        # et le système tolère les fautes de frappe.
        self.vectoriseur = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
        self.matrice = self.vectoriseur.fit_transform(textes)
        print(f"[KB] {len(self.entrees)} entrées chargées dans la base de connaissances")

    def _charger_faq(self, chemin):
        faq = json.loads(chemin.read_text(encoding="utf-8"))
        for cat in faq["categories"]:
            self.categories[cat["id"]] = cat["nom"]
            for q in cat["questions"]:
                self.entrees.append({
                    "id": q["id"],
                    "question": q["question"],
                    "reponse": q["reponse"],
                    "tags": q.get("tags", []),
                    "categorie": cat["id"],
                    "frequence": q.get("frequence", ""),
                })

    def _charger_procedures(self, chemin):
        procedures = json.loads(chemin.read_text(encoding="utf-8"))["procedures"]
        for proc in procedures:
            self.entrees.append({
                "id": proc["id"],
                "question": f"Comment faire : {proc['titre']} ? {proc.get('description', '')}",
                "libelle": f"Comment faire : {proc['titre']} ?",  # version courte, affichée en suggestion
                "reponse": formater_procedure(proc),
                "tags": [proc["titre"], proc["categorie"]],
                "categorie": CATEGORIE_PROCEDURE.get(proc["categorie"], "procedures_admin"),
                "frequence": "",
            })

    def _charger_annuaire(self, chemin):
        """Crée une entrée "contact et horaires" pour chaque service (US-006, US-007)."""
        annuaire = json.loads(chemin.read_text(encoding="utf-8"))
        for service in annuaire["services_administratifs"] + annuaire["services_etudiants"]:
            nom = service["service"]
            resp = service.get("responsable", {})
            lignes = [f"**{nom}**"]
            if service.get("horaires"):
                lignes.append(f"🕐 Horaires : {service['horaires']}")
            lieu = service.get("bureau") or service.get("localisation")
            if lieu:
                lignes.append(f"📍 Bureau : {lieu} ({service.get('batiment', 'campus')})")
            if resp.get("email"):
                lignes.append(f"📧 {resp['email']}")
            if resp.get("telephone"):
                lignes.append(f"☎️ {resp['telephone']}")
            if service.get("missions"):
                lignes.append("Missions : " + ", ".join(service["missions"]))
            self.entrees.append({
                "id": "CONTACT-" + normaliser(nom).split()[0].upper()[:10],
                "question": f"Comment contacter le service {nom} ? Horaires, email et téléphone {nom}",
                "libelle": f"Comment contacter le service {nom} ?",
                "reponse": "\n".join(lignes),
                "tags": ["contact", "horaires", "email", "téléphone", nom],
                "categorie": "services_campus",
                "frequence": "",
            })

    def rechercher(self, question, nb_resultats=3):
        """Renvoie les entrées les plus proches, avec leur score (0 à 1)."""
        vecteur = self.vectoriseur.transform([normaliser(question)])
        scores = cosine_similarity(vecteur, self.matrice)[0]
        meilleurs = scores.argsort()[::-1][:nb_resultats]  # indices triés du meilleur au moins bon
        return [(self.entrees[i], float(scores[i])) for i in meilleurs]

    def questions_frequentes(self, nb=6):
        """Questions les plus fréquentes de la FAQ (pour les suggestions, US-005)."""
        frequentes = [e for e in self.entrees if e["frequence"] == "très élevée"]
        return [e["question"] for e in frequentes[:nb]]
