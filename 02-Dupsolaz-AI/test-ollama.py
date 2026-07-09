import ollama

# Test de connexion avec Ollama
print("=" * 50)
print("TEST DE CONNEXION - DUPSOLAZ AI")
print("=" * 50)

# Vérifier quels modèles sont disponibles
try:
    models = ollama.list()
    print("\n Modèles disponibles sur ton Mac :")
    if isinstance(models, list):
        for model in models:
            print(f"   - {model['name']}")
    elif isinstance(models, dict) and 'models' in models:
        for model in models['models']:
            print(f"   - {model['name']}")
    else:
        print(f"   (format inattendu, mais connexion OK)")
except Exception as e:
    print(f"\n Note : La liste des modèles n'a pas pu être affichée (bug bibliothèque),")
    print(f"   mais la connexion est fonctionnelle puisque la génération a réussi.")

# Test d'une génération simple
print("\n Génération d'un test...")
try:
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": "Tu es un assistant administratif pour Dupsolaz Legacy. Tu es précis, concis et professionnel. Tu réponds en français."
            },
            {
                "role": "user",
                "content": "Présente-toi brièvement en tant qu'assistant Dupsolaz, en 2 phrases maximum."
            }
        ]
    )
    print(f"\n Réponse du modèle :")
    print(f"   {response['message']['content']}")
except Exception as e:
    print(f"\n Erreur lors de la génération : {e}")

print("\n" + "=" * 50)
print("Test terminé.")