from flask import Flask, render_template_string, request, jsonify
import json
import os
import ollama
from datetime import datetime

app = Flask(__name__)

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
FICHIER_CHECKLIST = os.path.join(DOSSIER_COURANT, "checklist.json")

# ============================================================
# CHECK-LIST PAR DÉFAUT
# ============================================================
CHECKLIST_DEFAUT = {
    "phases": [
        {
            "nom": "Avant le départ (Nouméa)",
            "taches": [
                {"libelle": "Créer un CV en anglais", "fait": False, "priorite": "haute"},
                {"libelle": "Obtenir un extrait de casier judiciaire (Crime Check)", "fait": False, "priorite": "haute"},
                {"libelle": "Vérifier validité du passeport (6 mois après arrivée)", "fait": False, "priorite": "haute"},
                {"libelle": "Souscrire assurance voyage PVT", "fait": False, "priorite": "haute"},
                {"libelle": "Imprimer visa grant notice", "fait": False, "priorite": "haute"},
                {"libelle": "Numériser tous les documents importants", "fait": False, "priorite": "moyenne"},
                {"libelle": "Prévenir la banque BCI du départ", "fait": False, "priorite": "moyenne"},
            ]
        },
        {
            "nom": "Arrivée à Sydney (Semaines 1-2)",
            "taches": [
                {"libelle": "Ouvrir compte bancaire Westpac", "fait": False, "priorite": "haute"},
                {"libelle": "Demander un TFN (Tax File Number)", "fait": False, "priorite": "haute"},
                {"libelle": "Acheter carte SIM Telstra", "fait": False, "priorite": "haute"},
                {"libelle": "Faire vérifier le Crime Check australien", "fait": False, "priorite": "haute"},
                {"libelle": "Obtenir une adresse postale stable", "fait": False, "priorite": "moyenne"},
                {"libelle": "S'inscrire à Medicare (si éligible)", "fait": False, "priorite": "moyenne"},
            ]
        },
        {
            "nom": "88 jours - Farm Work",
            "taches": [
                {"libelle": "Rechercher des fermes recrutant des backpackers", "fait": False, "priorite": "haute"},
                {"libelle": "Postuler aux offres de farm work", "fait": False, "priorite": "haute"},
                {"libelle": "Vérifier que l'employeur remplit le formulaire 1263", "fait": False, "priorite": "haute"},
                {"libelle": "Tenir un journal des jours travaillés", "fait": False, "priorite": "haute"},
                {"libelle": "Conserver toutes les fiches de paie", "fait": False, "priorite": "haute"},
            ]
        },
        {
            "nom": "Préparation 2ème visa / PR",
            "taches": [
                {"libelle": "Faire reconnaître ses diplômes (skills assessment)", "fait": False, "priorite": "haute"},
                {"libelle": "Préparer et passer l'IELTS (objectif 7.5)", "fait": False, "priorite": "haute"},
                {"libelle": "Rechercher des formations Dump Truck à Perth", "fait": False, "priorite": "moyenne"},
                {"libelle": "Constituer le dossier de demande de PR", "fait": False, "priorite": "haute"},
            ]
        }
    ],
    "derniere_maj": datetime.now().strftime("%Y-%m-%d")
}

# ============================================================
# FONCTIONS
# ============================================================
def charger_checklist():
    if not os.path.exists(FICHIER_CHECKLIST):
        with open(FICHIER_CHECKLIST, 'w') as f:
            json.dump(CHECKLIST_DEFAUT, f, indent=2)
        return CHECKLIST_DEFAUT
    with open(FICHIER_CHECKLIST, 'r') as f:
        return json.load(f)

def sauvegarder_checklist(data):
    data["derniere_maj"] = datetime.now().strftime("%Y-%m-%d")
    with open(FICHIER_CHECKLIST, 'w') as f:
        json.dump(data, f, indent=2)

def resumer_profil_australie():
    return """
PROFIL ISSAÏE - DÉPART AUSTRALIE :
- Point de chute : Sydney (2 semaines pour démarches admin)
- Phase 1 : 88 jours de farm work pour valider le 2ème visa
- Phase 2 : Emploi aérien (agent d'escale), agence de voyages, ou admin
- Phase 3 : Formation Dump Truck Operator à Perth, puis FIFO dans le Pilbara
- Objectif final : Résidence Permanente (PR) par travail qualifié ou reprise d'études
- IELTS cible : 7.5 minimum
- Compte bancaire cible : Westpac (AUD)
- Régions prioritaires : Sydney, NSW intérieur, Queensland rural, Perth, Pilbara, Kalgoorlie
"""

# ============================================================
# TEMPLATE HTML
# ============================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Australia AI - ATLAS OS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; display: flex; flex-direction: column; }
        .header { background: #16213e; padding: 20px; text-align: center; border-bottom: 3px solid #e94560; }
        .header h1 { color: #e94560; font-size: 24px; }
        .dashboard { max-width: 1000px; margin: 20px auto; padding: 0 20px; flex: 1; width: 100%; }
        .phase { background: #16213e; border-radius: 12px; padding: 18px; margin-bottom: 15px; border: 1px solid #0f3460; }
        .phase h3 { color: #e94560; margin-bottom: 10px; }
        .tache { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #0f3460; }
        .tache:last-child { border-bottom: none; }
        .tache input[type="checkbox"] { width: 18px; height: 18px; cursor: pointer; }
        .tache label { flex: 1; cursor: pointer; }
        .tache label.fait { text-decoration: line-through; color: #666; }
        .priorite-haute { color: #e94560; font-size: 12px; font-weight: bold; }
        .priorite-moyenne { color: #f0a500; font-size: 12px; }
        .progress { margin-bottom: 20px; background: #0f3460; border-radius: 8px; padding: 12px; }
        .progress-text { font-weight: bold; color: #4ecca3; }
        .progress-bar { background: #1a1a2e; border-radius: 10px; height: 10px; margin-top: 5px; overflow: hidden; }
        .progress-fill { background: #4ecca3; height: 100%; border-radius: 10px; transition: width 0.3s; }
        
        /* Chat */
        .chat-section { border-top: 2px solid #0f3460; padding: 0; background: #16213e; margin-top: 20px; }
        .chat-container { max-width: 1000px; margin: 0 auto; padding: 15px 20px; }
        .chat-messages { max-height: 250px; overflow-y: auto; margin-bottom: 10px; }
        .chat-msg { margin-bottom: 10px; padding: 10px 14px; border-radius: 10px; max-width: 80%; line-height: 1.4; font-size: 14px; }
        .chat-msg.user { background: #e94560; color: white; margin-left: auto; text-align: right; }
        .chat-msg.agent { background: #0f3460; color: #ddd; }
        .chat-input { display: flex; gap: 10px; }
        .chat-input input { flex: 1; padding: 10px 14px; border-radius: 20px; border: 1px solid #0f3460; background: #1a1a2e; color: #eee; font-size: 14px; outline: none; }
        .chat-input button { padding: 10px 20px; background: #e94560; color: white; border: none; border-radius: 20px; cursor: pointer; font-weight: bold; }
        .chat-input button:hover { background: #c23152; }
        .loading-msg { color: #888; font-style: italic; padding: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🦘 Australia AI</h1>
        <p style="opacity:0.7;">Check-list de départ & Assistant Australie — ATLAS OS</p>
    </div>
    
    <div class="dashboard">
        <div class="progress">
            <span class="progress-text" id="progressText">Progression : 0%</span>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill" style="width:0%"></div>
            </div>
        </div>
        
        <div id="phases"></div>
    </div>
    
    <div class="chat-section">
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="chat-msg agent">
                    🦘 G'day Isaïe ! Je suis Australia AI. Demande-moi par exemple :<br>
                    <em>"Quelles sont les démarches pour le 2ème visa ?"</em><br>
                    <em>"Quel est le salaire moyen d'un dump truck operator ?"</em><br>
                    <em>"Quelles régions pour les 88 jours ?"</em>
                </div>
            </div>
            <div class="chat-input">
                <input type="text" id="chatInput" placeholder="Pose ta question sur l'Australie..." onkeypress="if(event.key==='Enter') poserQuestion()">
                <button onclick="poserQuestion()">Demander</button>
            </div>
        </div>
    </div>
    
    <script>
        async function chargerChecklist() {
            const res = await fetch('/api/checklist');
            const data = await res.json();
            
            let totalTaches = 0;
            let tachesFaites = 0;
            
            let html = '';
            for (const phase of data.phases) {
                html += `<div class="phase"><h3>📋 ${phase.nom}</h3>`;
                for (let i = 0; i < phase.taches.length; i++) {
                    const tache = phase.taches[i];
                    totalTaches++;
                    if (tache.fait) tachesFaites++;
                    html += `
                        <div class="tache">
                            <input type="checkbox" id="${phase.nom}-${i}" ${tache.fait ? 'checked' : ''} onchange="toggleTache('${phase.nom}', ${i})">
                            <label for="${phase.nom}-${i}" class="${tache.fait ? 'fait' : ''}">${tache.libelle}</label>
                            <span class="priorite-${tache.priorite}">${tache.priorite.toUpperCase()}</span>
                        </div>`;
                }
                html += `</div>`;
            }
            document.getElementById('phases').innerHTML = html;
            
            const pourcentage = totalTaches > 0 ? Math.round((tachesFaites / totalTaches) * 100) : 0;
            document.getElementById('progressText').textContent = `Progression : ${pourcentage}% (${tachesFaites}/${totalTaches})`;
            document.getElementById('progressFill').style.width = pourcentage + '%';
        }
        
        async function toggleTache(phaseNom, tacheIndex) {
            await fetch('/api/toggle', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({phase: phaseNom, index: tacheIndex})
            });
            chargerChecklist();
        }
        
        async function poserQuestion() {
            const input = document.getElementById('chatInput');
            const question = input.value.trim();
            if (!question) return;
            
            const messages = document.getElementById('chatMessages');
            messages.innerHTML += `<div class="chat-msg user">${question}</div>`;
            messages.innerHTML += '<div class="chat-msg agent loading-msg" id="loadingMsg">🦘 Recherche en cours...</div>';
            messages.scrollTop = messages.scrollHeight;
            input.value = '';
            
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question})
                });
                const data = await res.json();
                
                document.getElementById('loadingMsg').remove();
                messages.innerHTML += `<div class="chat-msg agent">${data.reponse.replace(/\\n/g, '<br>')}</div>`;
                messages.scrollTop = messages.scrollHeight;
            } catch (e) {
                document.getElementById('loadingMsg').remove();
                messages.innerHTML += '<div class="chat-msg agent">❌ Erreur de connexion.</div>';
            }
        }
        
        chargerChecklist();
    </script>
</body>
</html>
"""

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/checklist')
def api_checklist():
    return jsonify(charger_checklist())

@app.route('/api/toggle', methods=['POST'])
def api_toggle():
    data = request.json
    phase_nom = data.get('phase')
    index = data.get('index')
    
    checklist = charger_checklist()
    for phase in checklist['phases']:
        if phase['nom'] == phase_nom:
            phase['taches'][index]['fait'] = not phase['taches'][index]['fait']
    
    sauvegarder_checklist(checklist)
    return jsonify({"ok": True})

@app.route('/api/chat', methods=['POST'])
def api_chat():
    question = request.json.get('question', '')
    profil = resumer_profil_australie()
    checklist = charger_checklist()
    
    # Résumé des tâches restantes
    taches_restantes = []
    for phase in checklist['phases']:
        for tache in phase['taches']:
            if not tache['fait']:
                taches_restantes.append(f"- [{tache['priorite'].upper()}] {tache['libelle']} ({phase['nom']})")
    
    try:
        response = ollama.chat(
            model="qwen2.5:7b",
            messages=[
                {
                    "role": "system",
                    "content": f"""Tu es Australia AI, l'assistant mobilité internationale d'Isaïe. Tu l'aides à préparer son départ en Australie.

{profil}

TÂCHES RESTANTES :
{chr(10).join(taches_restantes[:10])}

RÈGLES :
- Réponds en français, de façon concise et utile.
- Base-toi sur le profil d'Isaïe pour personnaliser tes réponses.
- Si tu ne sais pas quelque chose (ex: réglementation spécifique), dis-le honnêtement et suggère de vérifier sur immi.homeaffairs.gov.au.
- Pour les questions de salaire, donne des fourchettes réalistes en AUD.
- Encourage toujours la vérification officielle des informations.
- Rappelle les deadlines ou priorités quand c'est pertinent."""
                },
                {"role": "user", "content": question}
            ]
        )
        reponse = response['message']['content'].strip()
    except Exception as e:
        reponse = f"❌ Erreur Ollama. Détail : {e}"
    
    return jsonify({"reponse": reponse})

if __name__ == '__main__':
    print("🦘 Australia AI - Check-list & Assistant")
    print("http://127.0.0.1:5002")
    app.run(debug=True, host='127.0.0.1', port=5002)