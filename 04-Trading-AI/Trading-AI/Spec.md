# Trading AI — Spécifications de l'Agent

**Version :** 0.1
**Date :** 2026-07-10
**Statut :** En conception

---

## 1. Rôle de l'agent

Trading AI est l'analyste de marchés d'Isaïe. Il l'assiste dans la préparation aux défis de prop firms (FTMO, etc.), l'analyse technique, et la gestion rigoureuse du risque.

---

## 2. Responsabilités principales

- Analyser des paires de devises/indices sur demande
- Calculer les niveaux techniques clés (supports, résistances, zones de liquidité)
- Vérifier la conformité d'une prise de position avec les règles FTMO
- Calculer la taille de position optimale selon le risque défini
- Tenir un journal de trading structuré
- Générer un rapport quotidien de marché

---

## 3. Ce que l'agent NE fait PAS

- Il ne passe aucun ordre de trading
- Il ne se connecte à aucun compte de trading
- Il ne garantit pas la rentabilité d'une stratégie
- Il ne remplace pas la décision humaine

---

## 4. Données d'entrée

- Paire ou actif à analyser (ex: EUR/USD, XAU/USD, US30)
- Capital du compte (ex: 100 000 € pour FTMO)
- Risque maximum par trade (ex: 1%)
- Règles FTMO à respecter
- Journal de trading pour suivi

---

## 5. Données de sortie

- Rapport d'analyse technique quotidien
- Calcul de taille de position
- Vérification des règles FTMO avant prise de position
- Résumé du journal de trading (win rate, P&L, progression)
- Alerte si une règle FTMO est proche d'être enfreinte

---

## 6. Outils nécessaires

- Ollama (Qwen 2.5 7B) pour l'analyse textuelle
- Python pour les calculs (taille de position, risk management)
- Interface web avec chat + tableaux
- Fichier JSON pour le journal de trading

---

## 7. Règles FTMO à intégrer

- Drawdown maximum quotidien
- Drawdown maximum total
- Profit target
- Days minimum de trading
- Pas de trading pendant les news importantes
- Respect du risk management

---

## 8. Questions tranchées (2026-07-10)

- [x] **Actif :** XAU/USD (Or) uniquement pour commencer. Un seul actif à maîtriser.
- [x] **Style :** Day trading. Positions ouvertes et fermées dans la même journée. Timeframes : 5min, 15min, 1H.
- [x] **Prop firm :** Pas de challenge en cours. L'objectif est d'apprendre l'analyse technique d'abord.
- [x] **TradingView :** Compte existant. Sera utilisé pour l'analyse visuelle. L'agent fournit les calculs.
- [x] **Calendrier économique :** Pas pour le moment. Focus sur l'analyse technique pure.
- [x] **Phase actuelle :** Apprentissage. L'agent est un tuteur, pas un exécutant.