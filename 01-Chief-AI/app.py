from flask import Flask, render_template_string, request, jsonify
import ollama
import json
import os

app = Flask(__name__)

# ============================================================
# CALCULS FINANCIERS (Python uniquement, pas d'IA)
# ============================================================
def charger_finances():
    chemin = os.path.join(os.path.dirname(__file__), "..", "03-Finance-AI", "data", "finances.json")
    with open(chemin, 'r') as f:
        return json.load(f)

def calculer_strategie():
    donnees = charger_finances()
    taux_xpf = {"XPF": 1, "EUR": 119.33, "AUD": 72.46}
    
    solde_total = 0
    for compte in donnees["comptes"].values():
        if compte.get("actif", True):
            solde_total += compte["solde"] * taux_xpf.get(compte["devise"], 1)
    
    charges = sum(
        c["montant"] * taux_xpf.get(c["devise"], 1)
        for c in donnees["charges_fixes"]
        if c["frequence"] == "mensuelle"
    )
    
    enveloppe = 600000
    garantie = 340000
    a_reunir = enveloppe - garantie
    tarif = 5000
    heures = a_reunir / tarif
    mois = 8
    heures_semaine = heures / (mois * 4.33)
    revenu_ttc = a_reunir * 1.06
    
    return {
        "solde": round(solde_total),
        "charges": round(charges),
        "enveloppe": enveloppe,
        "garantie": garantie,
        "a_reunir": a_reunir,
        "tarif": tarif,
        "heures": round(heures, 1),
        "heures_semaine": round(heures_semaine, 1),
        "mois": mois,
        "revenu_ttc": round(revenu_ttc),
        "seuil": 100000,
        "projection": round(solde_total) - round(charges) + a_reunir
    }

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
        .dashboard { max-width: 900px; margin: 20px auto; padding: 0 20px; flex: 1; width: 100%; }
        .card { background: #16213e; border-radius: 12px; padding: 20px; margin-bottom: 15px; border: 1px solid #0f3460; }
        .card h3 { color: #e94560; margin-bottom: 10px; }
        .big-number { font-size: 36px; font-weight: bold; color: #4ecca3; }
        .highlight { color: #f0a500; font-weight: bold; }
        .row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #0f3460; }
        .row:last-child { border-bottom: none; }
        .chat-section { border-top: 2px solid #0f3460; padding: 20px; background: #16213e; margin-top: 20px; }
        .chat-messages { max-height: 200px; overflow-y: auto; margin-bottom: 10px; }
        .chat-msg { margin-bottom: 10px; padding: 10px 14px; border-radius: 10px; max-width: 85%; line-height: 1.4; font-size: 14px; }
        .chat-msg.user { background: #e94560; color: white; margin-left: auto; text-align: right; }
        .chat-msg.agent { background: #0f3460; color: #ddd; }
        .chat-input { display: flex; gap: 10px; }
        .chat-input input { flex: 1; padding: 12px 16px; border-radius: 20px; border: 1px solid #0f3460; background: #1a1a2e; color: #eee; font-size: 14px; outline: none; }
        .chat-input button { padding: 12px 24px; background: #e94560; color: white; border: none; border-radius: 20px; cursor: pointer; font-weight: bold; }
        .btn-refresh { padding: 10px 20px; background: #0f3460; color: #4ecca3; border: 1px solid #4ecca3; border-radius: 8px; cursor: pointer; margin-top: 10px; }
        .loading-msg { color: #888; font-style: italic; padding: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 ATLAS OS — Chief AI</h1>
        <p style="opacity:0.7;">Tableau de bord stratégique</p>
    </div>
    
    <div class="dashboard">
        <div class="card">
            <h3>🎯 Plan Départ Australie</h3>
            <div class="row"><span>Enveloppe Australie</span><span class="highlight" id="enveloppe">—</span></div>
            <div class="row"><span>Garantie après dépenses</span><span class="highlight" id="garantie">—</span></div>
            <div class="row"><span>Montant à réunir</span><span class="highlight" id="aReunir">—</span></div>
            <div class="row"><span>Tarif Dupsolaz</span><span id="tarif">—</span></div>
            <div class="row"><span>Heures de prestation nécessaires</span><span class="highlight" id="heures">—</span></div>
            <div class="row"><span>Soit par semaine (sur 8 mois)</span><span class="highlight" id="heuresSemaine">—</span></div>
            <div class="row"><span>Revenu TTC généré</span><span class="highlight" id="revenuTtc">—</span></div>
        </div>
        
        <div class="card">
            <h3>💰 Situation Financière</h3>
            <div class="row"><span>Solde total</span><span class="highlight" id="solde">—</span></div>
            <div class="row"><span>Charges mensuelles</span><span id="charges">—</span></div>
            <div class="row"><span>Seuil d'alerte</span><span id="seuil">—</span></div>
            <button class="btn-refresh" onclick="chargerDashboard()">🔄 Rafraîchir</button>
        </div>
    </div>
    
    <div class="chat-section" style="max-width:900px; margin:0 auto; width:100%;">
        <div class="chat-messages" id="chatMessages">
            <div class="chat-msg agent">
                💬 <strong>Mode Conseil</strong> : Pose une question sur l'Australie, les visas, ou Dupsolaz. Les calculs financiers sont affichés ci-dessus et sont 100% fiables (calculés par Python, pas par l'IA).
            </div>
        </div>
        <div class="chat-input">
            <input type="text" id="chatInput" placeholder="Ex: Quelles démarches pour le PVT ?" onkeypress="if(event.key==='Enter') poserQuestion()">
            <button onclick="poserQuestion()">Conseil</button>
        </div>
    </div>
    
    <script>
        async function chargerDashboard() {
            const res = await fetch('/api/dashboard');
            const d = await res.json();
            document.getElementById('enveloppe').textContent = d.enveloppe.toLocaleString() + ' XPF';
            document.getElementById('garantie').textContent = d.garantie.toLocaleString() + ' XPF';
            document.getElementById('aReunir').textContent = d.a_reunir.toLocaleString() + ' XPF';
            document.getElementById('tarif').textContent = d.tarif.toLocaleString() + ' XPF HT/h';
            document.getElementById('heures').textContent = d.heures + ' heures';
            document.getElementById('heuresSemaine').textContent = d.heures_semaine + ' h/semaine';
            document.getElementById('revenuTtc').textContent = d.revenu_ttc.toLocaleString() + ' XPF';
            document.getElementById('solde').textContent = d.solde.toLocaleString() + ' XPF';
            document.getElementById('charges').textContent = d.charges.toLocaleString() + ' XPF';
            document.getElementById('seuil').textContent = d.seuil.toLocaleString() + ' XPF';
        }
        
        async function poserQuestion() {
            const input = document.getElementById('chatInput');
            const question = input.value.trim();
            if (!question) return;
            
            const messages = document.getElementById('chatMessages');
            messages.innerHTML += `<div class="chat-msg user">${question}</div>`;
            messages.innerHTML += '<div class="chat-msg agent loading-msg" id="loadingMsg">🧠 Réflexion...</div>';
            messages.scrollTop = messages.scrollHeight;
            input.value = '';
            
            const res = await fetch('/api/conseil', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: question})
            });
            const data = await res.json();
            
            document.getElementById('loadingMsg').remove();
            messages.innerHTML += `<div class="chat-msg agent">${data.reponse.replace(/\\n/g, '<br>')}</div>`;
            messages.scrollTop = messages.scrollHeight;
        }
        
        chargerDashboard();
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

@app.route('/api/dashboard')
def dashboard():
    return jsonify(calculer_strategie())

@app.route('/api/conseil', methods=['POST'])
def conseil():
    question = request.json.get('question', '')
    strategie = calculer_strategie()
    
    try:
        response = ollama.chat(
            model="qwen2.5:7b",
            messages=[
                {
                    "role": "system",
                    "content": f"""Tu es Chief AI, conseiller pour Isaïe.

PROFIL : Isaïe prépare son départ en Australie dans 8 mois. Enveloppe : 600 000 XPF (dont 340 000 restants après dépenses). Il doit réunir 260 000 XPF via Dupsolaz (tarif : 5 000 XPF/h). Phases : Sydney → 88 jours farm → emploi aérien/admin → formation Dump Truck → PR.

RÈGLES : Réponds en français. Sois concis (8-10 lignes max). Appuie-toi sur le profil. N'invente pas de chiffres. Termine par un conseil concret."""
                },
                {"role": "user", "content": question}
            ]
        )
        reponse = response['message']['content'].strip()
    except:
        reponse = "❌ Ollama non disponible. Lance 'ollama serve'."
    
    return jsonify({"reponse": reponse})

if __name__ == '__main__':
    print("🧠 Chief AI - Tableau de bord stratégique")
    print("http://127.0.0.1:5003")
    app.run(debug=True, host='127.0.0.1', port=5003)