# ATLAS OS — Journal des Décisions Techniques

**Projet :** ATLAS OS
**Auteur :** Isaïe Mafileo (Dupsolaz)
**Date de création :** 2026-07-09

---

## Pourquoi ce journal ?

Toute décision technique, même minime, est notée ici avec la date et la raison. Dans six mois, quand on se demandera pourquoi on a choisi tel outil ou telle approche, ce document contiendra la réponse.

---

## Décisions

### 2026-07-09 — Création du projet ATLAS OS
**Décision :** Lancement du projet ATLAS OS.
**Contexte :** Besoin d'un système d'agents IA pour assister les activités professionnelles et personnelles.
**Conséquence :** Création de la structure de dossiers et du document de vision.

### 2026-07-09 — Compte GitHub : Dupsolaz
**Décision :** Création d'un compte GitHub sous le nom d'utilisateur Dupsolaz.
**Raison :** Héberger le code source, versionner le projet, et constituer un portfolio technique professionnel.

### 2026-07-09 — Structure du projet avec dossier 99-Archive
**Décision :** Utilisation de dossiers numérotés (00 à 99) pour la structure du projet.
**Raison :** Maintenir un ordre d'affichage logique. Le dossier 99-Archive permet de conserver l'historique sans encombrer l'espace de travail actif.

### 2026-07-09 — Premier outil : VS Code + GitHub
**Décision :** Utiliser Visual Studio Code comme éditeur principal, connecté à GitHub.
**Raison :** VS Code est l'outil standard pour le développement moderne. GitHub assure la sauvegarde et le versionnement.
### 2026-07-09 — Installation de l'environnement IA locale
**Décision :** Installation d'Ollama pour exécuter des modèles d'IA localement.
**Raison :** Exploiter la puissance de la puce Apple M4 (10.7 Go VRAM) sans dépendre du cloud, sans abonnement, et avec une confidentialité totale.
**Modèle choisi :** Llama 3.2 comme premier modèle léger et polyvalent.
**Test effectué :** Premier échange fonctionnel avec le modèle en local.

### 2026-07-09 — Spécifications Dupsolaz AI validées
**Décision :** Validation des spécifications fonctionnelles de Dupsolaz AI.
**Choix clés :** Interface web chat, génération DOCX + PDF, pas de CRM externe, templates issus de Canva, relecture interactive obligatoire.
**Conséquence :** Début de la collecte des modèles Canva et préparation du premier prototype.

### 2026-07-09 — Premier prototype Dupsolaz AI fonctionnel
**Décision :** Premier générateur de devis opérationnel avec Ollama et Python.
**Résultat :** Génération d'un devis JSON valide avec calcul automatique des montants, TGC à 6%, et distinction émetteur/client.
**Prochaines étapes :** Génération du DOCX à partir du JSON, interface web de chat, amélioration des templates.

### 2026-07-09 — Lancement conception Finance AI
**Décision :** Début de la conception de Finance AI, deuxième agent ATLAS OS.
**Choix clés :** Multi-devises (XPF, EUR, AUD), stockage JSON local, tableau de bord visuel, objectifs d'épargne ajustables, seuil d'alerte à 100 000 XPF.
**Conséquence :** Développement du prototype de gestion financière.

### 2026-07-09 — Finance AI opérationnel avec chat intelligent
**Décision :** Déploiement du tableau de bord Finance AI avec chat connecté à Ollama.
**Résultat :** Tableau de bord visuel multi-devises, calcul de projection 30 jours, système d'alerte, et chat capable d'analyser la situation financière pour répondre aux questions de type "Puis-je acheter X ?".
**Prochaines étapes :** Ajout des objectifs d'épargne, affinage des prompts, connexion à Australia AI.