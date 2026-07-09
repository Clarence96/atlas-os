import ollama
import json
from datetime import datetime, timedelta

# ============================================================
# CONFIGURATION DUPSOLAZ
# ============================================================
ENTREPRISE = {
    "nom": "Dupsolaz Legacy",
    "ridet": "TON_NUMERO_RIDET1 637 735.001",
    "forme_juridique": "Entreprise Individuelle",
    "adresse": "162 rue Edmond Mathey Mont-Dore",
    "email": "Dupsolaz0@gmail.com",
    "telephone": "+687 80 15 45",
    "logo": "Dupsolaz Legacy"
}

GRILLE_TARIFAIRE = {
    "secretariat": {"libelle": "Prestation de secrétariat", "unite": "heure", "tarif": 5000},
    "structuration": {"libelle": "Structuration d'entreprise", "unite": "jour", "tarif": 50000},
    "consulting": {"libelle": "Consulting", "unite": "heure", "tarif": 15000},
    "formation": {"libelle": "Formation", "unite": "heure", "tarif": 10000},
}

# ============================================================
# LE PROMPT SYSTÈME (le "cerveau" de l'agent)
# ============================================================
SYSTEM_PROMPT = """Tu es Dupsolaz AI, l'assistant administratif de Dupsolaz Legacy.
Ta mission : générer des devis professionnels à partir des informations fournies.

RÈGLES STRICTES :
- Tu réponds UNIQUEMENT en JSON valide, sans texte avant ni après.
- Les sauts de ligne dans les textes doivent utiliser \\n (double backslash) et jamais de caractères d'échappement fantaisistes.
- Le JSON doit être strictement valide. Pas de commentaires, pas de texte hors JSON.
- Les montants sont en Francs Pacifique (XPF).
- Les montants sont calculés automatiquement : quantité × tarif unitaire.
- La date d'échéance est calculée : date du jour + 30 jours.
- Le numéro de devis suit le format : DEV-AAAA-MM-NNN (ex: DEV-2026-07-001).
- Tu inclus TOUJOURS les conditions générales de Dupsolaz Legacy.
- La TGC (Taxe Générale sur la Consommation) est de 6% en Nouvelle-Calédonie.
- L'entreprise émettrice est Dupsolaz Legacy. Le client est la personne ou l'entité décrite dans la demande d'Isaïe.
- Ne confonds jamais l'émetteur du devis avec le destinataire.
- Si une information est manquante, tu mets "À COMPLÉTER" dans le champ.
- Tu ne discutes pas, tu ne commentes pas, tu produis le JSON.

STRUCTURE DU JSON ATTENDU :
{
    "numero_devis": "DEV-AAAA-MM-NNN",
    "date_emission": "AAAA-MM-JJ",
    "date_echeance": "AAAA-MM-JJ",
    "emetteur": {
        "nom": "Dupsolaz Legacy",
        "ridet": "...",
        "adresse": "...",
        "email": "...",
        "telephone": "..."
    },
    "client": {
        "nom": "Nom complet ou entreprise",
        "adresse": "Adresse complète",
        "email": "Email",
        "telephone": "Téléphone"
    },
    "prestations": [
        {
            "libelle": "Nom de la prestation",
            "quantite": nombre,
            "unite": "heure/jour/forfait",
            "tarif_unitaire": nombre,
            "montant": nombre
        }
    ],
    "total_ht": nombre,
    "tgc": 6,
    "total_ttc": nombre,
    "conditions": [
        "Condition 1",
        "Condition 2"
    ],
    "mentions_legales": "Texte des mentions légales"
}
"""

# ============================================================
# FONCTION PRINCIPALE
# ============================================================
def generer_devis(description_client: str) -> dict:
    """Génère un devis structuré à partir d'une description libre."""
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    prompt_utilisateur = f"""
Date du jour : {today}
Entreprise (émetteur du devis) : {json.dumps(ENTREPRISE, indent=2, ensure_ascii=False)}
Grille tarifaire : {json.dumps(GRILLE_TARIFAIRE, indent=2, ensure_ascii=False)}

Description de la mission par Isaïe :
\"\"\"
{description_client}
\"\"\"

Génère le devis complet au format JSON. Rappel : Dupsolaz Legacy est l'ÉMETTEUR, le client est le DESTINATAIRE.
"""
    
    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_utilisateur}
            ]
        )
        
        contenu = response['message']['content'].strip()
        
        # Nettoyage : certains modèles ajoutent des ```json ... ```
        if contenu.startswith("```"):
            contenu = contenu.split("\n", 1)[1]
            if contenu.endswith("```"):
                contenu = contenu.rsplit("\n", 1)[0]
        
        # Correction des échappements sauvages dans les chaînes
        contenu = contenu.replace('\n\\', '\\n')
        
        devis = json.loads(contenu)
        return devis
        
    except json.JSONDecodeError as e:
        return {"erreur": f"Le modèle n'a pas retourné un JSON valide. Détail : {e}", "reponse_brute": contenu}
    except Exception as e:
        return {"erreur": f"Erreur lors de la génération : {e}"}

# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("GÉNÉRATEUR DE DEVIS - DUPSOLAZ AI")
    print("=" * 60)
    
    # Test avec une description simple
    description_test = "Prestation de secrétariat pour le client Jean Dupont, 10 heures de travail, adresse email : jean@dupont.fr, adresse postale : 15 rue de Paris 75000 Paris, téléphone : 01 23 45 67 89"
    
    print(f"\n Description de la mission :")
    print(f"   {description_test}")
    
    print(f"\n Génération en cours...")
    devis = generer_devis(description_test)
    
    if "erreur" in devis:
        print(f"\n ERREUR : {devis['erreur']}")
        if "reponse_brute" in devis:
            print(f"\n Réponse brute du modèle :")
            print(devis['reponse_brute'])
    else:
        print(f"\n DEVIS GÉNÉRÉ :")
        print(json.dumps(devis, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)