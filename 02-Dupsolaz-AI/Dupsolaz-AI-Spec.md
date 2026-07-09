# Dupsolaz AI — Spécifications de l'Agent

**Version :** 0.1
**Date :** 2026-07-09
**Statut :** En conception

---

## 1. Rôle de l'agent

Dupsolaz AI est l'expert administratif et commercial de Dupsolaz Legacy. Il assiste Isaïe dans la création de documents professionnels standardisés, la gestion des clients et la conformité administrative des prestations.

---

## 2. Responsabilités principales

- Générer un devis professionnel à partir d'une description simple
- Transformer un devis accepté en contrat de prestation
- Générer une facture conforme à partir d'un contrat ou d'un bon de commande
- Créer des check-lists de suivi pour chaque mission
- Rédiger des emails clients contextuels (relance, confirmation, livraison)
- Suggérer des échéanciers de paiement réalistes

---

## 3. Ce que l'agent NE fait PAS

- Il ne signe rien à la place d'Isaïe
- Il n'envoie jamais un document sans validation humaine
- Il ne prend pas de décisions financières
- Il ne modifie pas les contrats déjà signés
- Il ne communique pas directement avec les clients

---

## 4. Données d'entrée

- Description textuelle de la mission par Isaïe
- Informations client (nom, adresse, contact)
- Type de prestation (secrétariat, structuration, consulting, etc.)
- Tarifs applicables (grille tarifaire Dupsolaz)
- Conditions générales de vente (CGV Dupsolaz)
- Modèles de documents existants (si disponibles)

---

## 5. Données de sortie

Pour chaque demande, l'agent produit :

1. **Un devis** au format PDF ou DOCX, prêt à être envoyé
2. **Un contrat** de prestation avec les clauses adaptées
3. **Une facture** avec mentions légales obligatoires
4. **Un échéancier** de paiement si nécessaire
5. **Un email d'accompagnement** personnalisé
6. **Une check-list** des actions à suivre pour la mission

---

## 6. Outils nécessaires

- Ollama (modèle local Llama 3.2 ou plus avancé)
- Bibliothèque Python pour la génération de documents (ex: python-docx, reportlab)
- Modèles de documents Dupsolaz (Canva, Word, ou Markdown)
- Accès aux CGV et grille tarifaire de Dupsolaz
- Interface en ligne de commande ou via n8n (à définir)

---

## 7. Règles métier strictes

1. Tout document généré doit inclure les mentions légales de Dupsolaz Legacy
2. Les montants sont toujours vérifiés avec la grille tarifaire officielle
3. Les dates d'échéance sont calculées automatiquement (ex: 30 jours date de facture)
4. Chaque document reçoit un numéro unique et séquentiel
5. Une copie de chaque document est sauvegardée dans l'archive Dupsolaz
6. Le logo et la charte graphique Dupsolaz sont obligatoires

---

## 8. Indicateurs de succès

- Un devis est généré en moins de 2 minutes après la demande
- Le taux d'erreur sur les montants est de 0%
- Les documents sont conformes aux modèles Dupsolaz à 100%
- Isaïe gagne au moins 50% de temps sur ses tâches administratives

---

## 9. Questions tranchées (2026-07-09)

- [x] **Interface :** Interface web de type chat, accessible localement sur le Mac. Combine la simplicité d'un chat avec le confort d'un navigateur.
- [x] **Format de sortie :** DOCX modifiable pour relecture et archivage, conversion en PDF après validation humaine explicite.
- [x] **CRM/Facturation :** Aucun outil externe. Dupsolaz AI intègre son propre système de numérotation séquentielle et d'archivage.
- [x] **Templates :** Les modèles Canva existants seront analysés et transformés en templates programmatiques. Isaïe fournira un devis et une facture anonymisés comme référence.
- [x] **Relecture :** Flux interactif obligatoire. L'agent propose un résumé, l'humain valide, l'agent génère le DOCX, l'humain relit, puis ordonne la conversion en PDF.

---

## 10. Prochaines étapes

1. Valider ce document de spécifications avec Isaïe
2. Collecter et standardiser les modèles de documents Dupsolaz
3. Formaliser la grille tarifaire dans un format exploitable par l'IA
4. Développer le premier prototype : génération de devis
5. Tester avec des cas réels de Dupsolaz Legacy