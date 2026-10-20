# 🎓 Assistant Virtuel Éducatif — ESIC

Chatbot pour le campus ESIC : répond aux questions des étudiants (emploi du temps, procédures, services, règlement), analyse les questions posées (dashboard Grafana) et simule une borne d'accueil interactive.

> Projet réalisé dans le cadre du projet de rentrée ESIS-2 / CPDIA-2.

## Structure du projet

```
assistant-virtuel-esic/
├── data/
│   ├── raw/      # données brutes fournies (non modifiées)
│   └── clean/    # données nettoyées, utilisées par le chatbot
├── docs/         # cahier des charges, rapport
└── scripts/      # scripts utilitaires (nettoyage des données…)
```

## Étapes réalisées

- [x] Nettoyage des données (`scripts/clean_data.py`)
- [ ] Sprint 1 — Chatbot MVP
- [ ] Sprint 2 — IA & Analytics
- [ ] Sprint 3 — Borne IoT & multilingue
