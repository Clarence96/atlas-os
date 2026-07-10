from flask import Flask, render_template_string, request, jsonify
import ollama
import json
import os
from datetime import datetime

app = Flask(__name__)

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
JOURNAL_FICHIER = os.path.join(DOSSIER_COURANT, "journal_trading.json")

# ============================================================
# JOURNAL DE TRADING
# ============================================================
def charger_journal():
    if not os.path.exists(JOURNAL_FICHIER):
        return {"trades": [], "capital_demo": 100000, "risque_par_trade_pct": 1}
    with open(JOURNAL_FICHIER, 'r') as f:
        return json.load(f)

def sauvegarder_journal(journal):
    with open(JOURNAL_FICHIER, 'w') as f:
        json.dump(journal, f, indent=2)

# ============================================================
# CALCULS TRADING (Python)
# ============================================================
def calculer_taille_position(capital, risque_pct, stop_loss_points, paire="XAUUSD"):
    """Calcule la taille de position optimale."""
    risque_montant = capital * (risque_pct / 100)
    # Pour XAU/USD : 1 point = 1 USD par lot standard
    valeur_point = 1
    taille_lot = risque_montant / (stop_loss_points * valeur_point)
    taille_lot = round(taille_lot, 2)
    if taille_lot < 0.01:
        taille_lot = 0.01
    return {
        "capital": capital,
        "risque_pct": risque_pct,
        "risque_montant": round(risque_montant, 2),
        "stop_loss_points": stop_loss_points,
        "taille_lot": taille_lot,
        "valeur_point": valeur_point
    }

def verifier_regles_ftmo(journal):
    """Vérifie les règles FTMO de base."""
    capital_demo = journal.get("capital_demo", 100000)
    perte_max_quotidienne = capital_demo * 0.05  # 5% max
    perte_max_totale = capital_demo * 0.10  # 10% max
    
    aujourdhui = datetime.now().strftime("%Y-%m-%d")
    perte_jour = 0
    perte_totale = 0
    
    for trade in journal["trades"]:
        pnl = trade.get("pnl", 0)
        perte_totale += pnl
        if trade.get("date") == aujourdhui:
            perte_jour += pnl
    
    alertes = []
    if perte_jour < -perte_max_quotidienne:
        alertes.append(f"⚠️ Limite quotidienne dépassée ({perte_jour:,.0f} / -{perte_max_quotidienne:,.0f})")
    if perte_totale < -perte_max_totale:
        alertes.append(f"⛔ Limite totale dépassée ({perte_totale:,.0f} / -{perte_max_totale:,.0f})")
    
    return {
        "perte_jour": round(perte_jour, 2),
        "perte_totale": round(perte_totale, 2),
        "limite_jour": round(perte_max_quotidienne, 2),
        "limite_totale": round(perte_max_totale, 2),
        "alertes": alertes,
        "nb_trades": len(journal["trades"])
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
    <title>Trading AI - ATLAS OS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; display: flex; flex-direction: column; }
        .header { background: #16213e; padding: 20px; text-align: center; border-bottom: 3px solid #f0a500; }
        .header h1 { color: #f0a500; font-size: 24px; }
        .dashboard { max-width: 1000px; margin: 20px auto; padding: 0 20px; flex: 1; width: 100%; }
        .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .card { background: #16213e; border-radius: 12px; padding: 18px; border: 1px solid #0f3460; }
        .card h3 { color: #f0a500; margin-bottom: 8px; font-size: 14px; text-transform: uppercase; }
        .card .big { font-size: 28px; font-weight: bold; }
        .card .sub { font-size: 12px; color: #888; margin-top: 4px; }
        .alert { background: #e94560; color: white; padding: 12px; border-radius: 8px; margin-bottom: 15px; }
        .ok { background: #0f3460; color: #4ecca3; padding: 12px; border-radius: 8px; margin-bottom: 15px; }
        .chat-section { border-top: 2px solid #0f3460; padding: 15px 20px; background: #16213e; }
        .chat-container { max-width: 1000px; margin: 0 auto; }
        .chat-messages { max-height: 250px; overflow-y: auto; margin-bottom: 10px; }
        .chat-msg { margin-bottom: 10px; padding: 10px 14px; border-radius: 10px; max-width: 85%; line-height: 1.4; font-size: 14px; }
        .chat-msg.user { background: #f0a500; color: #1a1a2e; margin-left: auto; }
        .chat-msg.agent { background: #0f3460; color: #ddd; }
        .chat-msg.agent .calc-box { background: #1a1a2e; padding: 10px; border-radius: 6px; margin-top: 8px; font-family: monospace; font-size: 13px; white-space: pre-line; }
        .chat-input { display: flex; gap: 10px; }
        .chat-input input { flex: 1; padding: 10px 14px; border-radius: 20px; border: 1px solid #0f3460; background: #1a1a2e; color: #eee; font-size: 14px; outline: none; }
        .chat-input button { padding: 10px 20px; background: #f0a500; color: #1a1a2e; border: none; border-radius: 20px; cursor: pointer; font-weight: bold; }
        .btn { padding: 8px 16px; background: #0f3460; color: #f0a500; border: 1px solid #f0a500; border-radius: 6px; cursor: pointer; font-size: 13px; margin-top: 10px; }
        .loading-msg { color: #888; font-style: italic; padding: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📈 Trading AI</h1>
        <p style="opacity:0.7;">Tuteur Day Trading — XAU/USD</p>
    </div>
    
    <div class="dashboard">
        <div id="alertes"></div>
        
        <div class="cards">
            <div class="card">
                <h3>💰 Capital Démo</h3>
                <div class="big" id="capital">—</div>
                <div class="sub">Risque par trade : <span id="risquePct">—</span>%</div>
            </div>
            <div class="card">
                <h3>📊 Trades enregistrés</h3>
                <div class="big" id="nbTrades">—</div>
                <div class="sub">Perte totale : <span id="perteTotale">—</span></div>
            </div>
            <div class="card">
                <h3>📉 Limite Jour</h3>
                <div class="big" id="limiteJour">—</div>
                <div class="sub">Perte du jour : <span id="perteJour">—</span></div>
            </div>
            <div class="card">
                <h3>🎯 Objectif FTMO</h3>
                <div class="big" style="color:#4ecca3;">10%</div>
                <div class="sub">Profit target phase 1</div>
            </div>
        </div>
        
        <button class="btn" onclick="chargerDashboard()">🔄 Rafraîchir</button>
    </div>
    
    <div class="chat-section">
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="chat-msg agent">
                    📈 <strong>Bonjour Isaïe !</strong> Je suis ton tuteur trading.<br><br>
                    <em>Exemples de questions :</em><br>
                    • "Calcule ma taille de position pour un stop à 20 points, capital 100 000 €"<br>
                    • "Explique-moi ce qu'est un support et une résistance"<br>
                    • "Qu'est-ce que le drawdown FTMO ?"<br>
                    • "Comment analyser XAU/USD en day trading ?"
                </div>
            </div>
            <div class="chat-input">
                <input type="text" id="chatInput" placeholder="Pose ta question trading..." onkeypress="if(event.key==='Enter') poserQuestion()">
                <button onclick="poserQuestion()">Demander</button>
            </div>
        </div>
    </div>
    
    <script>
        async function chargerDashboard() {
            const res = await fetch('/api/dashboard');
            const d = await res.json();
            
            document.getElementById('capital').textContent = d.capital_demo.toLocaleString() + ' $';
            document.getElementById('risquePct').textContent = d.risque_pct;
            document.getElementById('nbTrades').textContent = d.nb_trades;
            document.getElementById('perteTotale').textContent = d.perte_totale.toLocaleString() + ' $';
            document.getElementById('limiteJour').textContent = d.limite_jour.toLocaleString() + ' $';
            document.getElementById('perteJour').textContent = d.perte_jour.toLocaleString() + ' $';
            
            const alertesDiv = document.getElementById('alertes');
            if (d.alertes && d.alertes.length > 0) {
                alertesDiv.className = 'alert';
                alertesDiv.textContent = d.alertes.join(' | ');
            } else {
                alertesDiv.className = 'ok';
                alertesDiv.textContent = '✅ Aucune alerte FTMO. Règles respectées.';
            }
        }
        
        async function poserQuestion() {
            const input = document.getElementById('chatInput');
            const question = input.value.trim();
            if (!question) return;
            
            const messages = document.getElementById('chatMessages');
            messages.innerHTML += `<div class="chat-msg user">${question}</div>`;
            messages.innerHTML += '<div class="chat-msg agent loading-msg" id="loadingMsg">📈 Analyse...</div>';
            messages.scrollTop = messages.scrollHeight;
            input.value = '';
            
            const res = await fetch('/api/ask', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: question})
            });
            const data = await res.json();
            
            document.getElementById('loadingMsg').remove();
            let calcBox = '';
            if (data.calcul) {
                calcBox = `<div class="calc-box">📊 Calcul (Python, fiable à 100%) :
• Capital : ${data.calcul.capital.toLocaleString()} $
• Risque : ${data.calcul.risque_pct}% (${data.calcul.risque_montant.toLocaleString()} $)
• Stop Loss : ${data.calcul.stop_loss_points} points
• Taille de lot : ${data.calcul.taille_lot}</div>`;
            }
            messages.innerHTML += `<div class="chat-msg agent">${data.reponse.replace(/\\n/g, '<br>')}${calcBox}</div>`;
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
    journal = charger_journal()
    ftmo = verifier_regles_ftmo(journal)
    return jsonify({
        "capital_demo": journal["capital_demo"],
        "risque_pct": journal["risque_par_trade_pct"],
        "nb_trades": ftmo["nb_trades"],
        "perte_totale": ftmo["perte_totale"],
        "perte_jour": ftmo["perte_jour"],
        "limite_jour": ftmo["limite_jour"],
        "limite_totale": ftmo["limite_totale"],
        "alertes": ftmo["alertes"]
    })

@app.route('/api/ask', methods=['POST'])
def ask():
    question = request.json.get('question', '')
    journal = charger_journal()
    
    # Détection de demande de calcul
    calcul = None
    question_lower = question.lower()
    
    if any(mot in question_lower for mot in ["taille", "position", "lot", "stop", "calcul"]):
        # Extraire les paramètres basiques
        capital = journal["capital_demo"]
        risque_pct = journal["risque_par_trade_pct"]
        stop_loss = 20  # défaut
        
        # Essayer de trouver un stop loss dans la question
        mots = question.split()
        for i, mot in enumerate(mots):
            if mot.lower() in ["stop", "sl", "stoploss"] and i+1 < len(mots):
                try:
                    stop_loss = int(''.join(filter(str.isdigit, mots[i+1])))
                except:
                    pass
        
        calcul = calculer_taille_position(capital, risque_pct, stop_loss)
    
    try:
        response = ollama.chat(
            model="qwen2.5:7b",
            messages=[
                {
                    "role": "system",
                    "content": f"""Tu es Trading AI, un tuteur en day trading pour débutant.

CONTEXTE :
- Isaïe débute en trading. Il se concentre sur XAU/USD (Or) en day trading.
- Capital démo : {journal['capital_demo']:,} $
- Risque par trade : {journal['risque_par_trade_pct']}%
- Objectif futur : FTMO, mais d'abord apprendre l'analyse technique.

RÈGLES :
- Explique simplement, comme à un débutant. Évite le jargon sans le définir.
- Si la question est un calcul de position, le résultat exact est déjà fourni par Python.
- Pour les questions théoriques, sois pédagogue avec des exemples concrets sur XAU/USD.
- Ne donne pas de conseil d'achat ou de vente. Tu es un professeur, pas un conseiller financier.
- Réponds en 8-12 lignes max.
- Termine par une question pour vérifier la compréhension ou une suggestion d'exercice."""
                },
                {"role": "user", "content": question}
            ]
        )
        reponse = response['message']['content'].strip()
    except Exception as e:
        reponse = f"❌ Erreur Ollama. Détail : {e}"
    
    return jsonify({
        "reponse": reponse,
        "calcul": calcul
    })

if __name__ == '__main__':
    print("📈 Trading AI - Tuteur Day Trading")
    print("http://127.0.0.1:5004")
    app.run(debug=True, host='127.0.0.1', port=5004)