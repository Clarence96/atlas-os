from flask import Flask, render_template_string, request, jsonify
import ollama
import json

app = Flask(__name__)

# ============================================================
# PROFIL COMPLET D'ISAÏE (fourni à Chief AI)
# ============================================================
PROFIL_ISAIE = """
PROFIL COMPLET D'ISAÏE MAFILEO :

ENTREPRISE :
- Dupsolaz Legacy (EI)
- Services administratifs et structuration d'entreprise
- Basé à Mont-Dore, Nouméa, Nouvelle-Calédonie
- RIDET : 1 637 735.001
- Tarif horaire : à partir de 5 000 XPF HT selon le service
- Soumis à la TGC (6%) et non à la TVA

FINANCES :
- Compte BCI Courant (XPF)
- Compte BCI Épargne (XPF)
- Compte Revolut (EUR)
- Futur compte Westpac (AUD)
- Soumis à la TGC (6%) et non à la TVA
- Enveloppe Australie : 600 000 XPF (arrive dans 20 jours)
- Garantie après premières dépenses : environ 340 000 XPF pour tenir jusqu'au premier emploi (88 jours)
- Seuil d'alerte : 100 000 XPF 

PROJET AUSTRALIE :
- Départ prévu pour Sydney (2 semaines admin)
- Phase 1 : 88 jours de farm work pour 2ème visa
- Phase 2 : Emploi aérien/agence/admin pour fonds
- Phase 3 : Formation Dump Truck Operator à Perth
- Objectif final : Résidence Permanente (PR)
- IELTS cible : 7.5 minimum
- Régions : Sydney, NSW/QLD/VIC rural, Perth, Pilbara
- Budget Estimé nécessaire : 600 000 XPF

COMPÉTENCES :
- Secrétariat, administration, structuration d'entreprise
- Accueil, relation client, gestion administrative
- Expérience en gestion administrative et relation client
- Permis de conduire
- Informatique : VS Code, Python, Flutter, IA
- Langues : Français (natif), Anglais (bon niveau, cible 7.5 IELTS)
"""

# ============================================================
# DESCRIPTION DES AGENTS DISPONIBLES
# ============================================================
AGENTS = {
    "dupsolaz": {
        "nom": "Dupsolaz AI",
        "role": "Assistant administratif et commercial",
        "domaines": ["devis", "facture", "contrat", "client", "prestation", "secrétariat", "Dupsolaz", "TGC"],
        "port": 5000
    },
    "finance": {
        "nom": "Finance AI",
        "role": "Trésorier personnel",
        "domaines": ["argent", "compte", "solde", "budget", "épargne", "achat", "dépense", "XPF", "EUR", "AUD", "trésorerie", "projection"],
        "port": 5001
    },
    "australia": {
        "nom": "Australia AI",
        "role": "Assistant mobilité Australie",
        "domaines": ["Australie", "visa", "FIFO", "farm", "Perth", "Sydney", "IELTS", "PR", "Westpac", "démarche", "départ", "déménagement"],
        "port": 5002
    }
}

def detecter_agent(question):
    """Détecte quel(s) agent(s) sont pertinents pour la question."""
    question_lower = question.lower()
    agents_pertinents = []
    
    for agent_id, agent_info in AGENTS.items():
        for mot_cle in agent_info["domaines"]:
            if mot_cle.lower() in question_lower:
                agents_pertinents.append(agent_id)
                break
    
    # Si aucun mot-clé trouvé, on interroge tout le monde
    if not agents_pertinents:
        agents_pertinents = list(AGENTS.keys())
    
    return agents_pertinents

# ============================================================
# TEMPLATE HTML
# ============================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chief AI - ATLAS OS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #0a0a1a; color: #eee; min-height: 100vh; display: flex; flex-direction: column; }
        .header { background: linear-gradient(135deg, #1a1a3e, #0f3460); padding: 25px; text-align: center; border-bottom: 3px solid #e94560; }
        .header h1 { font-size: 28px; background: linear-gradient(90deg, #e94560, #f0a500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header .subtitle { opacity: 0.7; margin-top: 5px; }
        .agents-bar { display: flex; justify-content: center; gap: 15px; padding: 15px; background: #0f3460; flex-wrap: wrap; }
        .agent-badge { padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: bold; }
        .agent-badge.active { background: #4ecca3; color: #1a1a2e; }
        .agent-badge.inactive { background: #333; color: #888; }
        .chat-container { flex: 1; max-width: 900px; width: 100%; margin: 0 auto; padding: 20px; display: flex; flex-direction: column; }
        .chat-messages { flex: 1; overflow-y: auto; margin-bottom: 15px; }
        .chat-msg { margin-bottom: 15px; padding: 14px 18px; border-radius: 12px; max-width: 85%; line-height: 1.5; font-size: 15px; }
        .chat-msg.user { background: #e94560; color: white; margin-left: auto; text-align: right; }
        .chat-msg.chief { background: #16213e; border: 1px solid #0f3460; color: #ddd; }
        .chat-msg.chief .source { font-size: 11px; color: #f0a500; margin-top: 6px; font-style: italic; }
        .chat-input { display: flex; gap: 10px; }
        .chat-input input { flex: 1; padding: 14px 18px; border-radius: 25px; border: 1px solid #0f3460; background: #16213e; color: #eee; font-size: 15px; outline: none; }
        .chat-input input:focus { border-color: #e94560; }
        .chat-input button { padding: 14px 28px; background: linear-gradient(135deg, #e94560, #c23152); color: white; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; font-size: 15px; }
        .chat-input button:hover { opacity: 0.9; }
        .loading-msg { color: #888; font-style: italic; padding: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 ATLAS OS — Chief AI</h1>
        <p class="subtitle">Orchestrateur d'agents intelligents</p>
    </div>
    
    <div class="agents-bar">
        <span class="agent-badge inactive" id="badge-dupsolaz">📄 Dupsolaz AI</span>
        <span class="agent-badge inactive" id="badge-finance">💰 Finance AI</span>
        <span class="agent-badge inactive" id="badge-australia">🦘 Australia AI</span>
    </div>
    
    <div class="chat-container">
        <div class="chat-messages" id="chatMessages">
            <div class="chat-msg chief">
                🧠 Bonjour Isaïe. Je suis <strong>Chief AI</strong>, le coordinateur d'ATLAS OS.<br><br>
                Je peux interroger plusieurs agents en même temps pour répondre à tes questions complexes.<br><br>
                <em>Essaie par exemple :</em><br>
                • "Je pars en Australie dans 8 mois, quel est mon budget ?"<br>
                • "Combien de devis Dupsolaz dois-je faire pour financer mon départ ?"<br>
                • "Quelles démarches pour le visa et quel impact sur mes finances ?"
            </div>
        </div>
        
        <div class="chat-input">
            <input type="text" id="chatInput" placeholder="Pose ta question au Chief AI..." onkeypress="if(event.key==='Enter') poserQuestion()">
            <button onclick="poserQuestion()">Demander</button>
        </div>
    </div>
    
    <script>
        function activerBadges(agents) {
            document.getElementById('badge-dupsolaz').className = 'agent-badge ' + (agents.includes('dupsolaz') ? 'active' : 'inactive');
            document.getElementById('badge-finance').className = 'agent-badge ' + (agents.includes('finance') ? 'active' : 'inactive');
            document.getElementById('badge-australia').className = 'agent-badge ' + (agents.includes('australia') ? 'active' : 'inactive');
        }
        
        async function poserQuestion() {
            const input = document.getElementById('chatInput');
            const question = input.value.trim();
            if (!question) return;
            
            const messages = document.getElementById('chatMessages');
            messages.innerHTML += `<div class="chat-msg user">${question}</div>`;
            messages.innerHTML += '<div class="chat-msg chief loading-msg" id="loadingMsg">🧠 Analyse de la question et consultation des agents...</div>';
            messages.scrollTop = messages.scrollHeight;
            input.value = '';
            
            try {
                const res = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question})
                });
                const data = await res.json();
                
                document.getElementById('loadingMsg').remove();
                
                let sourcesHtml = '';
                if (data.agents_consultes && data.agents_consultes.length > 0) {
                    sourcesHtml = `<div class="source">Agents consultés : ${data.agents_consultes.join(', ')}</div>`;
                }
                
                messages.innerHTML += `<div class="chat-msg chief">${data.reponse.replace(/\\n/g, '<br>')}${sourcesHtml}</div>`;
                messages.scrollTop = messages.scrollHeight;
                
                activerBadges(data.agents_consultes || []);
            } catch (e) {
                document.getElementById('loadingMsg').remove();
                messages.innerHTML += '<div class="chat-msg chief">❌ Erreur de connexion au Chief AI.</div>';
            }
        }
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

@app.route('/api/ask', methods=['POST'])
def ask():
    question = request.json.get('question', '')
    
    # Détecter quels agents sont pertinents
    agents_pertinents = detecter_agent(question)
    
    # Construire le prompt pour Chief AI
    agents_description = "\n".join([
        f"- {AGENTS[a]['nom']} : {AGENTS[a]['role']} (domaines : {', '.join(AGENTS[a]['domaines'])})"
        for a in agents_pertinents
    ])
    
    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "system",
                    "content": f"""Tu es Chief AI, le coordinateur d'ATLAS OS.

PROFIL D'ISAÏE :
{PROFIL_ISAIE}

RÈGLES ABSOLUES :
1. Tu réponds en français, de façon concise.
2. Tu utilises UNIQUEMENT les chiffres du profil. Si un chiffre n'y est pas, dis "je ne sais pas".
3. Pour un calcul, tu poses l'opération clairement.
4. Pour une question d'argent, tu raisonnes en XPF.
5. Tu ne fais JAMAIS d'addition entre deux montants qui représentent la même chose.
6. Distingue bien : "enveloppe totale" (600 000 XPF) et "reste après dépenses" (340 000 XPF). Ce n'est pas 600 000 + 340 000 = 940 000. C'est 600 000 dont il restera 340 000 après dépenses.
7. Tarif Dupsolaz : à partir de 5000 XPF HT par heure.
8. Termine par UNE phrase de recommandation."""
                },
                {"role": "user", "content": f"Question d'Isaïe : {question}\n\nAgents pertinents détectés : {', '.join(agents_pertinents)}. Fournis une réponse unifiée."}
            ]
        )
        reponse = response['message']['content'].strip()
    except Exception as e:
        reponse = f"❌ Erreur Ollama. Détail : {e}"
    
    return jsonify({
        "reponse": reponse,
        "agents_consultes": [AGENTS[a]['nom'] for a in agents_pertinents]
    })

if __name__ == '__main__':
    print("🧠 Chief AI - Orchestrateur ATLAS OS")
    print("http://127.0.0.1:5003")
    app.run(debug=True, host='127.0.0.1', port=5003)