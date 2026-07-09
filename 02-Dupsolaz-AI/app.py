from flask import Flask, render_template_string, request, jsonify, send_file
import json
import os
import sys
import importlib.util

# Chargement manuel des modules du même dossier
dossier_courant = os.path.dirname(os.path.abspath(__file__))

def importer_module(nom_fichier, nom_module):
    chemin = os.path.join(dossier_courant, nom_fichier)
    spec = importlib.util.spec_from_file_location(nom_module, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

generateur_devis = importer_module("generateur-devis.py", "generateur_devis")
generateur_docx = importer_module("generateur-docx.py", "generateur_docx")

generer_devis = generateur_devis.generer_devis
generer_docx = generateur_docx.generer_docx

app = Flask(__name__)

# Template HTML intégré
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dupsolaz AI - Assistant Devis</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #003366;
            color: white;
            padding: 15px 20px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
        }
        .header span {
            font-weight: normal;
            font-size: 14px;
            opacity: 0.8;
        }
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            max-width: 800px;
            width: 100%;
            margin: 0 auto;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 80%;
            line-height: 1.5;
        }
        .message.user {
            background: #003366;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .message.agent {
            background: white;
            border: 1px solid #e0e0e0;
            color: #333;
        }
        .message.agent pre {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 8px;
            overflow-x: auto;
            margin-top: 8px;
            font-size: 13px;
        }
        .download-btn {
            display: inline-block;
            margin-top: 10px;
            padding: 10px 20px;
            background: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
        }
        .download-btn:hover {
            background: #218838;
        }
        .input-container {
            padding: 15px 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
            max-width: 800px;
            width: 100%;
            margin: 0 auto;
        }
        .input-container input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }
        .input-container input:focus {
            border-color: #003366;
        }
        .input-container button {
            padding: 12px 24px;
            background: #003366;
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 14px;
            cursor: pointer;
            font-weight: bold;
        }
        .input-container button:hover {
            background: #004080;
        }
        .loading {
            color: #888;
            font-style: italic;
            padding: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        🤖 Dupsolaz AI <span>| Générateur de Devis</span>
    </div>
    
    <div class="chat-container" id="chat">
        <div class="message agent">
            Bonjour Isaïe 👋<br>
            Je suis Dupsolaz AI, votre assistant administratif.<br><br>
            Décrivez-moi la mission et je génère un devis immédiatement.<br><br>
            <em>Exemple : « Prestation de secrétariat pour Jean Dupont, 10 heures, email : jean@dupont.fr, adresse : 15 rue de Paris 75000 Paris »</em>
        </div>
    </div>
    
    <div class="input-container">
        <input type="text" id="userInput" placeholder="Décrivez la mission..." onkeypress="if(event.key==='Enter') envoyer()">
        <button onclick="envoyer()">Générer</button>
    </div>
    
    <script>
        let dernierDevis = null;
        
        function ajouterMessage(contenu, type) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'message ' + type;
            div.innerHTML = contenu;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        
        function ajouterLoading() {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'message agent loading';
            div.id = 'loading';
            div.textContent = 'Génération du devis en cours...';
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        
        function retirerLoading() {
            const loading = document.getElementById('loading');
            if (loading) loading.remove();
        }
        
        async function envoyer() {
            const input = document.getElementById('userInput');
            const description = input.value.trim();
            if (!description) return;
            
            ajouterMessage(description, 'user');
            input.value = '';
            ajouterLoading();
            
            try {
                const response = await fetch('/generer', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({description: description})
                });
                
                const data = await response.json();
                retirerLoading();
                
                if (data.erreur) {
                    ajouterMessage('❌ ' + data.erreur + '<br><pre>' + (data.reponse_brute || '') + '</pre>', 'agent');
                } else {
                    dernierDevis = data.devis;
                    
                    let message = '✅ <b>Devis généré avec succès !</b><br><br>';
                    message += '<b>N° ' + data.devis.numero_devis + '</b><br>';
                    message += 'Client : ' + data.devis.client.nom + '<br>';
                    message += 'Total TTC : <b>' + data.devis.total_ttc.toLocaleString() + ' XPF</b><br>';
                    message += 'Échéance : ' + data.devis.date_echeance + '<br><br>';
                    message += '<a href="/telecharger/' + data.fichier + '" class="download-btn" download>📄 Télécharger le DOCX</a>';
                    
                    ajouterMessage(message, 'agent');
                }
            } catch (error) {
                retirerLoading();
                ajouterMessage('❌ Erreur de connexion au serveur.', 'agent');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generer', methods=['POST'])
def generer():
    data = request.json
    description = data.get('description', '')
    
    # Générer le devis JSON
    devis = generer_devis(description)
    
    if "erreur" in devis:
        return jsonify(devis)
    
    # Générer le DOCX
    nom_fichier = f"{devis.get('numero_devis', 'devis')}.docx"
    generer_docx(devis, nom_fichier)
    
    return jsonify({
        "devis": devis,
        "fichier": nom_fichier
    })

@app.route('/telecharger/<nom_fichier>')
def telecharger(nom_fichier):
    dossier = os.path.join(os.path.dirname(__file__), "documents_generees")
    chemin = os.path.join(dossier, nom_fichier)
    return send_file(chemin, as_attachment=True)

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 DUPSOLAZ AI - Interface Web")
    print("=" * 50)
    print("Ouvre http://127.0.0.1:5000 dans ton navigateur")
    app.run(debug=True, host='127.0.0.1', port=5000)