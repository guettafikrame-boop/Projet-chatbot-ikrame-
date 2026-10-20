"""
Nettoyage des données brutes (data/raw) vers des données propres (data/clean).

Pourquoi ce script ?
Les fichiers fournis contiennent des défauts qui empêchent un programme de les lire :
  1. faq_complete.json  : erreur de syntaxe JSON (un "]" en trop au milieu du fichier)
  2. emploi_du_temps.csv : 2 lignes parasites en tête, des ";;;;" en fin de ligne,
                           un mélange d'encodages (Windows-1252 + UTF-8)
  3. Les PDF (règlement, guide) : on extrait leur texte pour pouvoir le chercher plus tard

Utilisation (depuis la racine du projet) :
    python scripts/clean_data.py
"""

import csv
import io
import json
import re
import shutil
from pathlib import Path

from pypdf import PdfReader

# Path(__file__) = chemin de CE fichier. .parent.parent = remonter de 2 dossiers -> racine du projet
RACINE = Path(__file__).resolve().parent.parent
RAW = RACINE / "data" / "raw"
CLEAN = RACINE / "data" / "clean"


def nettoyer_faq():
    """Corrige la structure JSON de la FAQ puis vérifie qu'elle se charge."""
    texte = (RAW / "faq_complete.json").read_text(encoding="utf-8")

    # Le défaut : après la catégorie "procedures_admin", le tableau "categories" est fermé
    # par erreur ("],") alors que d'autres catégories suivent. On remplace
    #   }   ]   }   ],   {      par      }   ]   },   {
    # (\s* = "n'importe quels espaces ou retours à la ligne")
    texte_corrige, nb = re.subn(r"\}\s*\]\s*\}\s*\],\s*\{", "}\n      ]\n    },\n    {", texte)
    print(f"[FAQ] {nb} correction(s) de structure appliquée(s)")

    faq = json.loads(texte_corrige)  # plante si le JSON est encore invalide -> on le saurait tout de suite
    nb_questions = sum(len(cat["questions"]) for cat in faq["categories"])
    print(f"[FAQ] {len(faq['categories'])} catégories, {nb_questions} questions")

    # ensure_ascii=False garde les accents lisibles ; indent=2 rend le fichier joli
    (CLEAN / "faq.json").write_text(json.dumps(faq, ensure_ascii=False, indent=2), encoding="utf-8")


def decoder_ligne(octets):
    """Essaie l'UTF-8, sinon retombe sur l'encodage Windows (cp1252)."""
    try:
        return octets.decode("utf-8")
    except UnicodeDecodeError:
        return octets.decode("cp1252")


def nettoyer_csv():
    """Remet l'emploi du temps CSV au propre, en UTF-8."""
    lignes = [decoder_ligne(l).rstrip("\r\n") for l in (RAW / "emploi_du_temps.csv").read_bytes().splitlines()]

    # On cherche la vraie ligne d'en-tête (celle qui commence par "formation,")
    debut = next(i for i, l in enumerate(lignes) if l.startswith("formation,"))
    # On enlève les ";" en trop en fin de ligne et les lignes vides
    lignes_propres = [l.rstrip(";") for l in lignes[debut:] if l.strip(";").strip()]

    lecteur = csv.DictReader(io.StringIO("\n".join(lignes_propres)))
    creneaux = list(lecteur)
    print(f"[EDT] {len(creneaux)} créneaux, {len({c['groupe'] for c in creneaux})} groupes")

    with open(CLEAN / "emploi_du_temps.csv", "w", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=lecteur.fieldnames)
        ecrivain.writeheader()
        ecrivain.writerows(creneaux)


def extraire_pdf(nom_source, nom_sortie):
    """Extrait le texte brut d'un PDF dans un fichier .txt."""
    lecteur = PdfReader(RAW / nom_source)
    texte = "\n\n".join(page.extract_text() or "" for page in lecteur.pages)
    (CLEAN / nom_sortie).write_text(texte, encoding="utf-8")
    print(f"[PDF] {nom_source} : {len(lecteur.pages)} pages -> {nom_sortie}")


def copier_json_valides():
    """Les autres JSON sont déjà corrects : on vérifie puis on les copie."""
    for nom in ["annuaire_contacts.json", "emploi_du_temps.json", "procedures_esic.json"]:
        json.loads((RAW / nom).read_text(encoding="utf-8"))  # vérification
        shutil.copy(RAW / nom, CLEAN / nom)
        print(f"[JSON] {nom} valide, copié")


if __name__ == "__main__":
    CLEAN.mkdir(parents=True, exist_ok=True)
    nettoyer_faq()
    nettoyer_csv()
    copier_json_valides()
    extraire_pdf("reglement_interieur.pdf", "reglement_interieur.txt")
    extraire_pdf("guide_etudiant.pdf", "guide_etudiant.txt")
    print("✅ Données propres dans data/clean/")
