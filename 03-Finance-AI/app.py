from flask import Flask, render_template_string, request, jsonify
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
FICHIER_DONNEES = os.path.join(DOSSIER_COURANT, "data", "finances.json")
SEUIL_ALERTE_XPF = 100000

# Taux de change pour conversion vers XPF
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
        body { font-family: -apple-system, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; }
        .header { background: #16213e; padding: 20px; text-align: center; border-bottom: 2px solid #0f3460; }
        .header h1 { color: #e94560; font-size: 24px; }
        .dashboard { max-width: 1000px; margin: 20px auto; padding: 0 20px; }
        .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: #16213e; border-radius: 12px; padding: 20px; border: 1px solid #0f3460; }
        .card h3 { color: #e94560; margin-bottom: 10px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
        .card .montant { font-size: 32px; font-weight: bold; color: #fff; }
        .card .detail { font-size: 12px; color: #888; margin-top: 5px; }
        .alert { background: #e94560; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; }
        .ok { background: #0f3460; color: #4ecca3; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; }
        .comptes { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .compte { background: #0f3460; padding: 15px; border-radius: 8px; }
        .compte h4 { color: #e94560; margin-bottom: 5px; }
        .compte .solde { font-size: 22px; font-weight: bold; }
        .compte.inactif { opacity: 0.4; }
        .objectif { background: #16213e; padding: 12px; border-radius: 8px; margin-bottom: 8px; }
        .progress-bar { background: #0f3460; border-radius: 10px; height: 10px; margin-top: 5px; overflow: hidden; }
        .progress-fill { background: #4ecca3; height: 100%; border-radius: 10px; }
        .btn { padding: 8px 16px; background: #e94560; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; }
        .btn:hover { background: #c23152; }
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
                <h3>💎 Solde Total (XPF)</h3>
                <div class="montant" id="soldeTotal">—</div>
                <div class="detail">Tous comptes confondus</div>
            </div>
            <div class="card">
                <h3>📉 Charges Mensuelles</h3>
                <div class="montant" id="chargesMensuelles">—</div>
                <div class="detail">Charges fixes par mois</div>
            </div>
            <div class="card">
                <h3>📈 Projection 30 jours</h3>
                <div class="montant" id="projection">—</div>
                <div class="detail">Solde projeté dans 30 jours</div>
            </div>
            <div class="card">
                <h3>📊 Reste à vivre</h3>
                <div class="montant" id="resteAVivre">—</div>
                <div class="detail">Après charges, avant revenus</div>
            </div>
        </div>
        
        <h3 style="margin-bottom:15px;">🏦 Comptes</h3>
        <div class="comptes" id="comptes"></div>
        
        <h3 style="margin-bottom:15px;">🎯 Objectifs d'épargne</h3>
        <div id="objectifs"></div>
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
                        <div style="font-size:12px;color:#888;">${compte.type} ${!compte.actif ? '(inactif)' : ''}</div>
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
                        <span style="font-size:12px;color:#888;">${obj.cible.toLocaleString()} ${obj.devise}</span>
                    </div>`;
            }
            document.getElementById('objectifs').innerHTML = objHtml || '<p style="color:#888;">Aucun objectif défini. Ajoutez-en dans finances.json.</p>';
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
        alerte = f"Attention : solde projeté à {projection:,.0f} XPF dans 30 jours (sous le seuil de {SEUIL_ALERTE_XPF:,.0f} XPF)"
    
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

if __name__ == '__main__':
    print("💰 Finance AI - Tableau de bord")
    print("http://127.0.0.1:5001")
    app.run(debug=True, host='127.0.0.1', port=5001)