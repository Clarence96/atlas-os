# Australia AI — Spécifications de l'Agent

**Version :** 0.1
**Date :** 2026-07-09
**Statut :** En conception

---

## 1. Rôle de l'agent

Australia AI est l'agent de veille et de préparation pour le départ d'Isaïe en Australie. Il surveille les opportunités professionnelles, les évolutions des visas, et prépare la logistique du départ.

---

## 2. Responsabilités principales

- Surveiller les offres d'emploi FIFO correspondant au profil d'Isaïe
- Identifier les entreprises qui sponsorisent des visas
- Suivre les métiers en demande (skilled occupation lists)
- Alerter sur les changements de réglementation des visas
- Comparer les salaires par région et par secteur
- Préparer des check-lists pour le départ (documents, démarches)

---

## 3. Ce que l'agent NE fait PAS

- Il ne postule pas à ta place
- Il ne prend pas de décisions sur ta carrière
- Il ne garantit pas l'exactitude des offres (vérification humaine nécessaire)
- Il ne remplace pas un agent de migration

---

## 4. Données d'entrée

- Profil professionnel d'Isaïe (CV, compétences, certifications)
- Régions cibles (Australie occidentale, Queensland, etc.)
- Types de postes recherchés (FIFO, mines, construction, admin)
- Sources d'offres d'emploi (Seek, Indeed, LinkedIn)
- Sites gouvernementaux australiens (immi.homeaffairs.gov.au)

---

## 5. Données de sortie

- Liste des offres correspondant au profil, mise à jour régulièrement
- Alertes sur les nouvelles offres pertinentes
- Rapport sur les entreprises qui sponsorisent
- Tableau des salaires moyens par métier et région
- Échéancier des démarches administratives

---

## 6. Questions tranchées (2026-07-09)

- [x] **Veille :** Automatique. L'agent scrapera les sources ou utilisera des API. Pas de recherche manuelle.
- [x] **Métiers ciblés :** 3 phases — (1) Farm work 88 jours, (2) Agent d'escale / agence voyages / admin, (3) Dump Truck Operator FIFO. Objectif final : PR par travail qualifié ou reprise d'études.
- [x] **Régions :** Sydney (arrivée), zones rurales NSW/QLD/VIC (88 jours), Perth (formation + FIFO), Pilbara/Kalgoorlie (zones minières).
- [x] **CV anglais :** Pas encore créé. L'agent le signalera dans les check-lists. Learning AI s'en chargera.
- [x] **Coût de vie :** Module intégré pour comparer logement + transport par zone géographique.