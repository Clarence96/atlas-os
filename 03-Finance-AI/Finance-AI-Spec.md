# Finance AI — Spécifications de l'Agent

**Version :** 0.1
**Date :** 2026-07-09
**Statut :** En conception

---

## 1. Rôle de l'agent

Finance AI est le trésorier personnel et professionnel d'Isaïe. Il assure le suivi de la trésorerie, analyse les flux financiers, et répond aux questions de type "Puis-je me permettre cette dépense ?" avec des chiffres, pas des impressions.

---

## 2. Responsabilités principales

- Suivre les soldes des comptes bancaires
- Catégoriser les dépenses et revenus
- Projeter la trésorerie à 30, 60 et 90 jours
- Alerter sur les découverts potentiels
- Répondre à des questions du type : "Si tel client paie dans X jours, puis-je acheter Y ?"
- Générer un rapport financier mensuel simple

---

## 3. Ce que l'agent NE fait PAS

- Il n'effectue aucune transaction bancaire
- Il ne se connecte jamais directement à une banque sans validation humaine
- Il ne remplace pas un expert-comptable
- Il ne juge pas les dépenses, il les expose

---

## 4. Données d'entrée (Phase 1 - Manuelle)

Pour le prototype, les données sont saisies manuellement par Isaïe :

- Soldes des comptes (courant, épargne, espèces)
- Charges fixes mensuelles (loyer, abonnements, prêts, etc.)
- Revenus attendus (clients, échéances, montants)
- Dépenses ponctuelles prévues

---

## 5. Données de sortie

- Tableau de trésorerie prévisionnelle
- Réponse chiffrée à une question de type "Puis-je me permettre ?"
- Alerte si le solde projeté passe sous un seuil défini
- Rapport mensuel : entrées, sorties, reste à vivre

---

## 6. Outils nécessaires

- Ollama (Llama 3.2)
- Python (json, datetime)
- Fichier JSON pour stocker les données financières
- Interface web (similaire à Dupsolaz AI)

---

## 7. Questions tranchées (2026-07-09)

- [x] **Seuil d'alerte :** 100 000 XPF. L'agent alerte si le solde projeté passe sous ce seuil.
- [x] **Devises :** Multi-devises. XPF (BCI Nouvelle-Calédonie), EUR (Revolut), AUD (Westpac à venir).
- [x] **Stockage :** Fichier JSON local dans 03-Finance-AI/data/. Les données sensibles (numéros de compte) seront cryptées à part.
- [x] **Interface :** Tableau de bord visuel avec graphiques par devise et vue globale consolidée.
- [x] **Objectifs d'épargne :** Système ajustable. Création, modification et suivi de progression des objectifs.