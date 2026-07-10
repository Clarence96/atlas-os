from flask import Flask, render_template_string, request, jsonify
import ollama
import json
import os
from datetime import datetime

app = Flask(__name__)

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
FICHIER_NOTES = os.path.join(DOSSIER_COURANT, "notes.json")
FICHIER_RAPPELS = os.path.join(DOSSIER_COURANT, "rappels.json")

def charger_json(chemin, defaut):
    if not os.path.exists(chemin):
        with open(chemin, 'w') as f:
            json.dump(defaut, f)
        return defaut
    with open(chemin, 'r') as f:
        return json.load(f)

def sauvegarder_json(chemin, data):
    with open(chemin, 'w') as f:
        json.dump(data, f, indent=2)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Personal AI - ATLAS OS</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#1a1a2e;color:#eee;min-height:100vh;display:flex;flex-direction:column}
.header{background:#16213e;padding:20px;text-align:center;border-bottom:3px solid #9b59b6}
.header h1{color:#9b59b6;font-size:24px}
.dashboard{max-width:800px;margin:20px auto;padding:0 20px;flex:1;width:100%}
.clock{text-align:center;margin-bottom:20px}
.clock .time{font-size:48px;font-weight:bold;color:#fff}
.clock .date{font-size:18px;color:#9b59b6;margin-top:5px}
.motivation{background:linear-gradient(135deg,#2d1b4e,#16213e);padding:18px;border-radius:12px;text-align:center;margin-bottom:20px;font-style:italic;font-size:16px;border:1px solid #9b59b6}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-bottom:20px}
.card{background:#16213e;border-radius:12px;padding:16px;border:1px solid #0f3460}
.card h3{color:#9b59b6;margin-bottom:10px;font-size:14px;text-transform:uppercase}
.card textarea{width:100%;height:100px;background:#0f3460;border:1px solid #333;color:#eee;padding:10px;border-radius:8px;font-family:inherit;resize:vertical;font-size:13px}
.card input{width:100%;padding:8px 12px;background:#0f3460;border:1px solid #333;color:#eee;border-radius:6px;margin-bottom:6px;font-size:13px}
.btn{padding:8px 16px;background:#9b59b6;color:white;border:none;border-radius:6px;cursor:pointer;font-weight:bold;font-size:13px;margin-top:5px}
.btn:hover{opacity:0.9}
.btn-del{background:#e94560;margin-left:5px;padding:4px 10px;font-size:11px}
.rappel-item{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #0f3460;font-size:13px}
.chat-section{border-top:2px solid #0f3460;padding:15px 20px;background:#16213e;margin-top:20px}
.chat-container{max-width:800px;margin:0 auto}
.chat-messages{max-height:200px;overflow-y:auto;margin-bottom:10px}
.chat-msg{margin-bottom:10px;padding:10px 14px;border-radius:10px;max-width:85%;line-height:1.4;font-size:14px}
.chat-msg.user{background:#9b59b6;color:white;margin-left:auto}
.chat-msg.agent{background:#0f3460;color:#ddd}
.chat-input{display:flex;gap:10px}
.chat-input input{flex:1;padding:10px 14px;border-radius:20px;border:1px solid #0f3460;background:#1a1a2e;color:#eee;font-size:14px;outline:none}
.chat-input button{padding:10px 20px;background:#9b59b6;color:white;border:none;border-radius:20px;cursor:pointer;font-weight:bold}
.loading-msg{color:#888;font-style:italic;padding:10px}
</style>
</head>
<body>
<div class="header"><h1>🤝 Personal AI</h1><p style="opacity:0.7">Assistant personnel — ATLAS OS</p></div>
<div class="dashboard">
<div class="clock"><div class="time" id="clock">--:--</div><div class="date" id="date">---</div></div>
<div class="motivation" id="motivation">Chargement...</div>
<div class="cards">
<div class="card"><h3>📝 Notes rapides</h3><textarea id="notes" placeholder="Ecris tes notes ici..."></textarea><button class="btn" onclick="sauverNotes()">💾 Sauvegarder</button></div>
<div class="card"><h3>⏰ Rappels</h3><input type="text" id="rappelInput" placeholder="Nouveau rappel..."><input type="date" id="rappelDate"><button class="btn" onclick="ajouterRappel()">+ Ajouter</button><div id="rappelsList" style="margin-top:10px"></div></div>
</div>
</div>
<div class="chat-section"><div class="chat-container">
<div class="chat-messages" id="chatMessages"><div class="chat-msg agent">🤝 <strong>Bonjour Isaie !</strong> Je suis ton assistant personnel. Parle-moi de tout : motivation, conseils, organisation, bien-etre, ou simplement discuter.</div></div>
<div class="chat-input"><input type="text" id="chatInput" placeholder="Parle-moi..." onkeypress="if(event.key==='Enter')poserQuestion()"><button onclick="poserQuestion()">Envoyer</button></div>
</div></div>
<script>
function updateClock(){
    var now=new Date();
    document.getElementById('clock').textContent=now.toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit'});
    document.getElementById('date').textContent=now.toLocaleDateString('fr-FR',{weekday:'long',day:'numeric',month:'long',year:'numeric'});
}
updateClock();setInterval(updateClock,1000);

async function chargerDashboard(){
    try{
        var n=await fetch('/api/notes');var nd=await n.json();
        document.getElementById('notes').value=nd.contenu||'';
        var r=await fetch('/api/rappels');var rd=await r.json();
        var h='';
        rd.rappels.forEach(function(rappel,i){
            h+='<div class="rappel-item"><span>'+rappel.texte+' <small style="color:#9b59b6">('+rappel.date+')</small></span><button class="btn btn-del" onclick="supprimerRappel('+i+')">X</button></div>';
        });
        document.getElementById('rappelsList').innerHTML=h||'<span style="color:#888">Aucun rappel</span>';
        var m=await fetch('/api/motivation');var md=await m.json();
        document.getElementById('motivation').textContent=md.phrase;
    }catch(e){}
}
chargerDashboard();

async function sauverNotes(){
    var contenu=document.getElementById('notes').value;
    await fetch('/api/notes',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({contenu:contenu})});
    alert('Notes sauvegardees !');
}

async function ajouterRappel(){
    var texte=document.getElementById('rappelInput').value.trim();
    var date=document.getElementById('rappelDate').value;
    if(!texte||!date)return;
    await fetch('/api/rappels',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({texte:texte,date:date})});
    document.getElementById('rappelInput').value='';
    document.getElementById('rappelDate').value='';
    chargerDashboard();
}

async function supprimerRappel(index){
    await fetch('/api/rappels/'+index,{method:'DELETE'});
    chargerDashboard();
}

async function poserQuestion(){
    var input=document.getElementById('chatInput');
    var q=input.value.trim();
    if(!q)return;
    var msg=document.getElementById('chatMessages');
    msg.innerHTML+='<div class="chat-msg user">'+q+'</div>';
    msg.innerHTML+='<div class="chat-msg agent loading-msg" id="loadMsg">🤝 Reflexion...</div>';
    msg.scrollTop=msg.scrollHeight;
    input.value='';
    try{
        var r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
        var d=await r.json();
        document.getElementById('loadMsg').remove();
        msg.innerHTML+='<div class="chat-msg agent">'+d.reponse.replace(/\\n/g,'<br>')+'</div>';
        msg.scrollTop=msg.scrollHeight;
    }catch(e){
        document.getElementById('loadMsg').remove();
        msg.innerHTML+='<div class="chat-msg agent">Erreur de connexion.</div>';
    }
}
</script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/notes', methods=['GET'])
def get_notes():
    return jsonify(charger_json(FICHIER_NOTES, {"contenu": ""}))

@app.route('/api/notes', methods=['POST'])
def save_notes():
    data = request.json
    sauvegarder_json(FICHIER_NOTES, data)
    return jsonify({"ok": True})

@app.route('/api/rappels', methods=['GET'])
def get_rappels():
    return jsonify(charger_json(FICHIER_RAPPELS, {"rappels": []}))

@app.route('/api/rappels', methods=['POST'])
def add_rappel():
    data = request.json
    rappels = charger_json(FICHIER_RAPPELS, {"rappels": []})
    rappels["rappels"].append({"texte": data["texte"], "date": data["date"]})
    sauvegarder_json(FICHIER_RAPPELS, rappels)
    return jsonify({"ok": True})

@app.route('/api/rappels/<int:index>', methods=['DELETE'])
def delete_rappel(index):
    rappels = charger_json(FICHIER_RAPPELS, {"rappels": []})
    if 0 <= index < len(rappels["rappels"]):
        rappels["rappels"].pop(index)
        sauvegarder_json(FICHIER_RAPPELS, rappels)
    return jsonify({"ok": True})

@app.route('/api/motivation')
def motivation():
    try:
        response = ollama.chat(model="qwen2.5:7b", messages=[
            {"role": "system", "content": "Genere UNE phrase de motivation inspirante en francais. Sois original, pas de citation celebre. Maximum 15 mots. Reponds uniquement avec la phrase, rien d'autre."}
        ])
        phrase = response['message']['content'].strip()
    except:
        phrase = "Chaque jour est une nouvelle opportunite de progresser."
    return jsonify({"phrase": phrase})

@app.route('/api/chat', methods=['POST'])
def chat():
    question = request.json.get('question', '')
    try:
        response = ollama.chat(model="qwen2.5:7b", messages=[
            {"role": "system", "content": "Tu es Personal AI, l'assistant personnel d'Isaie. Il a 29 ans, prepare son depart en Australie, est chef d'entreprise (Dupsolaz Legacy). Sois bienveillant, encourageant, utile. Parle de tout : motivation, organisation, bien-etre, conseils de vie. Reponds en francais, 5-10 lignes max. Termine par une question ou une suggestion."},
            {"role": "user", "content": question}
        ])
        return jsonify({"reponse": response['message']['content'].strip()})
    except Exception as e:
        return jsonify({"reponse": f"Desole, je rencontre un probleme technique. Reessaie plus tard."})

if __name__ == '__main__':
    print("🤝 Personal AI - Assistant personnel")
    print("http://127.0.0.1:5006")
    app.run(debug=True, host='127.0.0.1', port=5006)