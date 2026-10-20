# 🎓 Assistant Virtuel Éducatif — ESIC

Chatbot pour le campus ESIC : il répond aux questions des étudiants (emplois du temps, procédures, services, règlement), analyse les questions posées (dashboard Grafana) et simule une borne d'accueil interactive.

> Projet réalisé dans le cadre du projet de rentrée ESIS-2 / CPDIA-2. Les données sont fictives, créées pour le projet.

## 🚀 Lancer le projet

Prérequis : **Docker Desktop** (ouvert) et **Git**. Rien d'autre à installer.

```bash
docker compose up --build
```

| Service | Adresse |
|---|---|
| 💬 Chat (frontend React) | http://localhost:5173 |
| ⚙️ API (backend Flask) | http://localhost:5001/api/health |
| 📜 Derniers échanges enregistrés | http://localhost:5001/api/logs |

Arrêter : `Ctrl + C`, puis `docker compose down`.

## 🏗️ Architecture

```
┌──────────────┐  HTTP/JSON  ┌──────────────────┐   SQL   ┌──────────────┐
│  Frontend    │ ──────────▶ │  Backend Flask   │ ──────▶ │  PostgreSQL  │
│  React+Vite  │             │  + TF-IDF        │         │  (logs)      │
│  :5173       │ ◀────────── │  :5001           │         │              │
└──────────────┘             └──────────────────┘         └──────────────┘
                                     │ lit
                                     ▼
                              data/clean/ (FAQ, procédures, annuaire…)
```

## 📁 Structure

```
├── backend/
│   ├── app.py              # routes de l'API (Flask)
│   ├── chatbot.py          # logique de réponse (seuils, politesse, secours)
│   ├── knowledge_base.py   # chargement des données + recherche TF-IDF
│   ├── security.py         # validation, anti-injection, limitation de débit
│   └── database.py         # enregistrement des échanges dans PostgreSQL
├── frontend/src/
│   ├── App.jsx             # interface du chat
│   ├── TexteFormate.jsx    # affichage sécurisé des réponses (gras, puces)
│   └── App.css             # styles (responsive + mode sombre)
├── db/init.sql             # création de la table "conversations"
├── data/raw/               # données brutes fournies (jamais modifiées)
├── data/clean/             # données nettoyées (scripts/clean_data.py)
└── docker-compose.yml      # lance les 3 conteneurs
```

## ✅ Avancement

- [x] Nettoyage des données (`scripts/clean_data.py`)
- [x] **Sprint 1 — Chatbot MVP**
  - [x] US-001 Question en langage naturel → réponse (192 entrées : FAQ + procédures + annuaire)
  - [x] US-002 Historique de la conversation dans la session
  - [x] US-003 Redémarrer une conversation
  - [x] US-004 Interface responsive (mobile + desktop)
  - [x] US-005 Suggestions de questions fréquentes
  - [x] US-006 à US-010 Horaires, contacts, règles, dates, formations
  - [x] US-011 Enregistrement horodaté de chaque question (PostgreSQL)
  - [x] US-012 Filtrage des injections (prompt, SQL, XSS, commandes)
  - [x] US-013 Limitation à 10 questions / minute / utilisateur
  - [x] Bandeau RGPD, identifiant de session anonyme
- [ ] Sprint 2 — IA & Analytics
- [ ] Sprint 3 — Borne IoT & multilingue
