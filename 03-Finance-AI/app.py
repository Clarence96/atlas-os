from flask import Flask, render_template_string, request, jsonify
import json
import os
import ollama
from datetime import datetime, timedelta

app = Flask(__name__)

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
FICHIER_DONNEES = os.path.join(DOSSIER_COURANT, "data", "finances.json")
SEUIL_ALERTE_XPF = 100000

TAUX_VERS_XPF = {
    "XPF": 1,
    "EUR": 119.33,
    "AUD": 72.46
}

# ============================================================
# FONCTIONS FINANCIÈRES
# ============================================================

def charger_donnees():
    with open(FICHIER_DONNEES, 'r') as f:
        return json.load(f)

def sauvegarder_donnees(donnees):
    with open(FICHIER_DONNEES, 'w') as f:
        json.dump(donnees, f, indent=2)

def convertir_en_xpf(montant, devise):
    return montant * TAUX_VERS_XPF.get(devise, 1)

def calculer_solde_total_xpf(donnees):
    total = 0
    for compte in donnees["comptes"].values():
        if compte.get("actif", True):
            total += convertir_en_xpf(compte["solde"], compte["devise"])
    return total

def calculer_charges_mensuelles_xpf(donnees):
    total = 0
    for charge in donnees["charges_fixes"]:
        if charge["frequence"] == "mensuelle":
            total += convertir_en_xpf(charge["montant"], charge["devise"])
    return total

def calculer_revenus_prevus_30j(donnees):
    total = 0
    aujourdhui = datetime.now().date()
    for revenu in donnees.get("revenus_attendus", []):
        date_prevue = datetime.strptime(revenu["date"], "%Y-%m-%d").date()
        if aujourdhui <= date_prevue <= aujourdhui + timedelta(days=30):
            total += convertir_en_xpf(revenu["montant"], revenu["devise"])
    return total

def calculer_projection_30j(donnees):
    solde = calculer_solde_total_xpf(donnees)
    charges = calculer_charges_mensuelles_xpf(donnees)
    revenus = calculer_revenus_prevus_30j(donnees)
    return solde + revenus - charges

def calculer_progression_objectifs(donnees):
    resultats = []
    for obj in donnees.get("objectifs_epargne", []):
        total_epargne = 0
        for compte in donnees["comptes"].values():
            if compte["devise"] == obj["devise"]:
                total_epargne += compte["solde"]
        progression = (total_epargne / obj["montant_cible"]) * 100 if obj["montant_cible"] > 0 else 0
        resultats.append({
            "nom": obj["nom"],
            "cible": obj["montant_cible"],
            "devise": obj["devise"],
            "progression": round(progression, 1)
        })
    return resultats

def resumer_finances_pour_ia(donnees):
    """Prépare un résumé des finances pour le prompt IA."""
    solde_total = calculer_solde_total_xpf(donnees)
    charges = calculer_charges_mensuelles_xpf(donnees)
    projection = calculer_projection_30j(donnees)
    
    resume = f"""
SITUATION FINANCIÈRE D'ISAÏE :
- Solde total : {solde_total:,.0f} XPF
- Charges mensuelles : {charges:,.0f} XPF
- Projection 30 jours : {projection:,.0f} XPF
- Seuil d'alerte : {SEUIL_ALERTE_XPF:,.0f} XPF

COMPTES :
"""
    for id_compte, compte in donnees["comptes"].items():
        if compte.get("actif", True):
            resume += f"- {compte['nom']} : {compte['solde']:,.2f} {compte['devise']}\n"
    
    resume += "\nCHARGES FIXES MENSUELLES :\n"
    for charge in donnees["charges_fixes"]:
        resume += f"- {charge['libelle']} : {charge['montant']:,.0f} {charge['devise']}\n"
    
    resume += "\nREVENUS ATTENDUS :\n"
    for revenu in donnees.get("revenus_attendus", []):
        resume += f"- {revenu['libelle']} : {revenu['montant']:,.0f} {revenu['devise']} (prévu le {revenu['date']})\n"
    
    if not donnees.get("revenus_attendus"):
        resume += "(aucun revenu enregistré)\n"
    
    resume += "\nOBJECTIFS D'ÉPARGNE :\n"
    objectifs = calculer_progression_objectifs(donnees)
    for obj in objectifs:
        resume += f"- {obj['nom']} : {obj['progression']}% atteint (cible : {obj['cible']:,} {obj['devise']})\n"
    
    if not objectifs:
        resume += "(aucun objectif défini)\n"
    
    return resume

# ============================================================
# TEMPLATE HTML
# ============================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Finance AI - ATLAS OS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; display: flex; flex-direction: column; }
        .header { background: #16213e; padding: 20px; text-align: center; border-bottom: 2px solid #0f3460; }
        .header h1 { color: #e94560; font-size: 24px; }
        .dashboard { max-width: 1000px; margin: 20px auto; padding: 0 20px; flex: 1; width: 100%; }
        .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .card { background: #16213e; border-radius: 12px; padding: 18px; border: 1px solid #0f3460; }
        .card h3 { color: #e94560; margin-bottom: 8px; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }
        .card .montant { font-size: 28px; font-weight: bold; color: #fff; }
        .card .detail { font-size: 11px; color: #888; margin-top: 4px; }
        .alert { background: #e94560; color: white; padding: 12px; border-radius: 8px; margin-bottom: 15px; font-weight: bold; font-size: 14px; }
        .ok { background: #0f3460; color: #4ecca3; padding: 12px; border-radius: 8px; margin-bottom: 15px; font-weight: bold; font-size: 14px; }
        .comptes { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 20px; }
        .compte { background: #0f3460; padding: 14px; border-radius: 8px; }
        .compte h4 { color: #e94560; margin-bottom: 4px; }
        .compte .solde { font-size: 20px; font-weight: bold; }
        .compte.inactif { opacity: 0.4; }
        .objectif { background: #16213e; padding: 10px; border-radius: 8px; margin-bottom: 6px; }
        .progress-bar { background: #0f3460; border-radius: 10px; height: 8px; margin-top: 4px; overflow: hidden; }
        .progress-fill { background: #4ecca3; height: 100%; border-radius: 10px; }
        
        /* Chat */
        .chat-section { border-top: 2px solid #0f3460; padding: 0; background: #16213e; }
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
        <h1>💰 Finance AI</h1>
        <p style="opacity:0.7;">Tableau de bord financier — ATLAS OS</p>
    </div>
    
    <div class="dashboard">
        <div id="alerte"></div>
        
        <div class="cards">
            <div class="card">
                <h3>💎 Solde Total</h3>
                <div class="montant" id="soldeTotal">—</div>
                <div class="detail">Tous comptes (XPF)</div>
            </div>
            <div class="card">
                <h3>📉 Charges /mois</h3>
                <div class="montant" id="chargesMensuelles">—</div>
                <div class="detail">Fixes mensuelles</div>
            </div>
            <div class="card">
                <h3>📈 Projection 30j</h3>
                <div class="montant" id="projection">—</div>
                <div class="detail">Dans 30 jours</div>
            </div>
            <div class="card">
                <h3>📊 Reste à vivre</h3>
                <div class="montant" id="resteAVivre">—</div>
                <div class="detail">Après charges</div>
            </div>
        </div>
        
        <div class="comptes" id="comptes"></div>
        
        <h4 style="color:#e94560; margin-bottom:10px;">🎯 Objectifs d'épargne</h4>
        <div id="objectifs" style="margin-bottom:15px;"></div>
    </div>
    
    <div class="chat-section">
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="chat-msg agent">
                    💬 Bonjour Isaïe ! Je connais ta situation financière. Demande-moi par exemple :<br>
                    <em>"Puis-je acheter un Mac à 300 000 XPF ?"</em><br>
                    ou <em>"Combien me reste-t-il après le loyer ?"</em>
                </div>
            </div>
            <div class="chat-input">
                <input type="text" id="chatInput" placeholder="Pose ta question..." onkeypress="if(event.key==='Enter') poserQuestion()">
                <button onclick="poserQuestion()">Demander</button>
            </div>
        </div>
    </div>
    
    <script>
        async function chargerDashboard() {
            const res = await fetch('/api/dashboard');
            const data = await res.json();
            
            document.getElementById('soldeTotal').textContent = data.solde_total.toLocaleString() + ' XPF';
            document.getElementById('chargesMensuelles').textContent = data.charges_mensuelles.toLocaleString() + ' XPF';
            document.getElementById('projection').textContent = data.projection_30j.toLocaleString() + ' XPF';
            document.getElementById('resteAVivre').textContent = data.reste_a_vivre.toLocaleString() + ' XPF';
            
            const alerte = document.getElementById('alerte');
            if (data.alerte) {
                alerte.className = 'alert';
                alerte.textContent = '⚠️ ' + data.alerte;
            } else {
                alerte.className = 'ok';
                alerte.textContent = '✅ Trésorerie au-dessus du seuil de sécurité';
            }
            
            let comptesHtml = '';
            for (const [id, compte] of Object.entries(data.comptes)) {
                comptesHtml += `
                    <div class="compte ${!compte.actif ? 'inactif' : ''}">
                        <h4>${compte.nom}</h4>
                        <div class="solde">${compte.solde.toLocaleString()} ${compte.devise}</div>
                        <div style="font-size:11px;color:#888;">${compte.type} ${!compte.actif ? '(inactif)' : ''}</div>
                    </div>`;
            }
            document.getElementById('comptes').innerHTML = comptesHtml;
            
            let objHtml = '';
            for (const obj of data.objectifs) {
                objHtml += `
                    <div class="objectif">
                        <strong>${obj.nom}</strong> — ${obj.progression}%
                        <div class="progress-bar">
                            <div class="progress-fill" style="width:${Math.min(obj.progression, 100)}%"></div>
                        </div>
                        <span style="font-size:11px;color:#888;">${obj.cible.toLocaleString()} ${obj.devise}</span>
                    </div>`;
            }
            document.getElementById('objectifs').innerHTML = objHtml || '<p style="color:#888;font-size:13px;">Aucun objectif défini.</p>';
        }
        
        async function poserQuestion() {
            const input = document.getElementById('chatInput');
            const question = input.value.trim();
            if (!question) return;
            
            const messages = document.getElementById('chatMessages');
            messages.innerHTML += `<div class="chat-msg user">${question}</div>`;
            messages.innerHTML += '<div class="chat-msg agent loading-msg" id="loadingMsg">🤔 Analyse en cours...</div>';
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
    donnees = charger_donnees()
    solde_total = calculer_solde_total_xpf(donnees)
    charges = calculer_charges_mensuelles_xpf(donnees)
    projection = calculer_projection_30j(donnees)
    reste_a_vivre = solde_total - charges
    
    alerte = None
    if projection < SEUIL_ALERTE_XPF:
        alerte = f"Solde projeté à {projection:,.0f} XPF dans 30 jours (sous le seuil de {SEUIL_ALERTE_XPF:,.0f} XPF)"
    
    objectifs = calculer_progression_objectifs(donnees)
    
    return jsonify({
        "solde_total": round(solde_total),
        "charges_mensuelles": round(charges),
        "projection_30j": round(projection),
        "reste_a_vivre": round(reste_a_vivre),
        "alerte": alerte,
        "comptes": donnees["comptes"],
        "objectifs": objectifs
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    question = request.json.get('question', '')
    donnees = charger_donnees()
    resume = resumer_finances_pour_ia(donnees)
    
    try:
        response = ollama.chat(
            model="qwen2.5:7b",
            messages=[
                {
                    "role": "system",
                    "content": f"""Tu es Finance AI, le trésorier personnel d'Isaïe. Tu connais sa situation financière.

{resume}

RÈGLES STRICTES :
- Réponds en français, de façon concise et utile.
- Appuie-toi UNIQUEMENT sur les données fournies ci-dessus.
- Si tu manques d'informations, dis-le honnêtement.
- Les montants sont en Francs Pacifique (XPF) sauf indication contraire.
- Pour toute question de type "Puis-je acheter X ?", suis cette méthode :
  1. Regarde le solde total actuel.
  2. Regarde la projection à 30 jours.
  3. Si le solde total est déjà négatif, réponds que c'est impossible sans nouvelle rentrée d'argent.
  4. Si le solde est positif mais que la dépense fait passer la projection sous le seuil d'alerte, préviens du risque.
  5. Si le solde est positif et que la dépense laisse la projection au-dessus du seuil, donne ton feu vert.
- Ne dis jamais qu'une dépense est possible si le solde est négatif.
- Mentionne toujours les chiffres exacts.
- Termine par une recommandation claire : "Faisable", "Risqué", ou "Impossible"."""
                },
                {"role": "user", "content": question}
            ]
        )
        reponse = response['message']['content'].strip()
    except Exception as e:
        reponse = f"❌ Erreur : Impossible de contacter Ollama. Vérifie que le serveur est lancé (ollama serve). Détail : {e}"
    
    return jsonify({"reponse": reponse})

if __name__ == '__main__':
    print("💰 Finance AI - Tableau de bord + Chat")
    print("http://127.0.0.1:5001")
    app.run(debug=True, host='127.0.0.1', port=5001)