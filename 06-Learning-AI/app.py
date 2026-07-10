from flask import Flask, render_template_string, request, jsonify
import ollama
import json
import os
from datetime import datetime
import re

app = Flask(__name__)

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
FICHIER_PROGRES = os.path.join(DOSSIER_COURANT, "progres.json")

def charger_progres():
    if not os.path.exists(FICHIER_PROGRES):
        return {"quiz_passes": 0, "score_total": 0, "moyenne": 0, "sujets_etudies": [], "derniere_session": None, "points_faibles": [], "objectif_ielts": 7.5, "date_debut": datetime.now().strftime("%Y-%m-%d"), "historique": []}
    with open(FICHIER_PROGRES, 'r') as f:
        return json.load(f)

def sauvegarder_progres(progres):
    with open(FICHIER_PROGRES, 'w') as f:
        json.dump(progres, f, indent=2)

def reinitialiser_progres():
    progres = {"quiz_passes": 0, "score_total": 0, "moyenne": 0, "sujets_etudies": [], "derniere_session": None, "points_faibles": [], "objectif_ielts": 7.5, "date_debut": datetime.now().strftime("%Y-%m-%d"), "historique": []}
    sauvegarder_progres(progres)
    return progres

def enregistrer_quiz(score, sujet):
    progres = charger_progres()
    progres["quiz_passes"] += 1
    progres["score_total"] += score
    progres["moyenne"] = round(progres["score_total"] / progres["quiz_passes"], 1)
    progres["derniere_session"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    if sujet not in progres["sujets_etudies"]:
        progres["sujets_etudies"].append(sujet)
    if score < 6 and sujet not in progres["points_faibles"]:
        progres["points_faibles"].append(sujet)
    progres["historique"].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "sujet": sujet, "score": score})
    if len(progres["historique"]) > 50:
        progres["historique"] = progres["historique"][-50:]
    sauvegarder_progres(progres)
    return progres

# Lire le template depuis un fichier séparé pour éviter les conflits de guillemets
TEMPLATE_PATH = os.path.join(DOSSIER_COURANT, "template.html")

TEMPLATE_CONTENU = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Learning AI - ATLAS OS</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#1a1a2e;color:#eee;min-height:100vh;display:flex;flex-direction:column}
.header{background:#16213e;padding:20px;text-align:center;border-bottom:3px solid #4ecca3}
.header h1{color:#4ecca3;font-size:24px}
.dashboard{max-width:1000px;margin:20px auto;padding:0 20px;flex:1;width:100%}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin-bottom:20px}
.card{background:#16213e;border-radius:12px;padding:18px;border:1px solid #0f3460}
.card h3{color:#4ecca3;margin-bottom:8px;font-size:13px;text-transform:uppercase}
.card .big{font-size:28px;font-weight:bold}
.card .sub{font-size:12px;color:#888;margin-top:4px}
.tabs{display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap}
.tab{padding:10px 20px;border-radius:20px;cursor:pointer;font-weight:bold;border:1px solid #0f3460;background:#16213e;color:#eee}
.tab.active{background:#4ecca3;color:#1a1a2e;border-color:#4ecca3}
.quiz-container{background:#16213e;border-radius:12px;padding:20px;border:1px solid #0f3460;margin-bottom:20px}
.question{font-size:16px;margin-bottom:15px;font-weight:bold}
.options{display:flex;flex-direction:column;gap:8px}
.option{padding:12px 16px;background:#0f3460;border-radius:8px;cursor:pointer;border:1px solid transparent}
.option:hover{border-color:#4ecca3}
.option.selected{border-color:#4ecca3;background:#1a3a1a}
.btn{padding:12px 24px;background:#4ecca3;color:#1a1a2e;border:none;border-radius:8px;cursor:pointer;font-weight:bold;font-size:15px;margin-top:15px}
.btn:hover{opacity:0.9}
.btn-small{padding:6px 12px;background:#0f3460;color:#e94560;border:1px solid #e94560;border-radius:6px;cursor:pointer;font-size:11px;margin-left:10px}
.result{padding:15px;border-radius:8px;margin-top:15px;font-weight:bold;text-align:center;font-size:18px}
.result.good{background:#1a3a1a;color:#4ecca3}
.result.ok{background:#3a3a1a;color:#f0a500}
.result.bad{background:#3a1a1a;color:#e94560}
.evolution-bar{display:flex;align-items:flex-end;gap:4px;height:80px;padding-top:10px;overflow-x:auto}
.chat-section{border-top:2px solid #0f3460;padding:15px 20px;background:#16213e}
.chat-container{max-width:1000px;margin:0 auto}
.chat-messages{max-height:200px;overflow-y:auto;margin-bottom:10px}
.chat-msg{margin-bottom:10px;padding:10px 14px;border-radius:10px;max-width:85%;line-height:1.4;font-size:14px}
.chat-msg.user{background:#4ecca3;color:#1a1a2e;margin-left:auto}
.chat-msg.agent{background:#0f3460;color:#ddd}
.chat-input{display:flex;gap:10px}
.chat-input input{flex:1;padding:10px 14px;border-radius:20px;border:1px solid #0f3460;background:#1a1a2e;color:#eee;font-size:14px;outline:none}
.chat-input button{padding:10px 20px;background:#4ecca3;color:#1a1a2e;border:none;border-radius:20px;cursor:pointer;font-weight:bold}
.loading-msg{color:#888;font-style:italic;padding:10px}
.correction-box{background:#1a1a2e;padding:12px;border-radius:8px;margin-bottom:8px;border-left:3px solid #e94560}
.correction-box .explanation{color:#ccc;margin-top:5px;display:block;line-height:1.5}
</style>
</head>
<body>
<div class="header"><h1>📚 Learning AI</h1><p style="opacity:0.7">Tuteur IELTS & Culture Generale</p></div>
<div class="dashboard">
<div class="cards">
<div class="card"><h3>📊 Quiz passes</h3><div class="big" id="quizPasses">0</div><div class="sub">Moyenne : <span id="moyenne">0</span>/5</div></div>
<div class="card"><h3>🎯 Objectif IELTS</h3><div class="big" style="color:#4ecca3" id="objectifIelts">7.5</div><div class="sub">Score cible</div></div>
<div class="card"><h3>📅 Derniere session</h3><div class="big" style="font-size:18px" id="derniereSession">Aucune</div><div class="sub">Points faibles : <span id="pointsFaibles">—</span></div></div>
</div>
<div class="card" style="margin-bottom:20px"><h3>📈 Evolution des scores <button class="btn-small" onclick="reinitialiserScores()">🗑 Reinitialiser</button></h3><div class="evolution-bar" id="evolution"></div><div class="sub">Derniers quiz (sur 5)</div></div>
<div class="tabs">
<div class="tab active" id="tabIelts" onclick="changerSujet('ielts')">🎓 IELTS</div>
<div class="tab" id="tabTrading" onclick="changerSujet('trading')">📈 Trading</div>
<div class="tab" id="tabGeneral" onclick="changerSujet('general')">🌍 Culture G</div>
</div>
<div class="quiz-container" id="quizBox">
<div class="question" id="question">Clique sur "Nouveau Quiz" pour commencer</div>
<div class="options" id="options"></div>
<button class="btn" id="btnQuiz" onclick="actionQuiz()">🎲 Nouveau Quiz (5 questions)</button>
<div id="result"></div>
</div>
</div>
<div class="chat-section"><div class="chat-container">
<div class="chat-messages" id="chatMessages"><div class="chat-msg agent">📚 <strong>Bonjour Isaie !</strong> Je suis ton tuteur.<br><em>Demande-moi :</em><br>• "Explique-moi le present perfect"<br>• "Donne-moi un exercice d'ecriture IELTS"<br>• "C'est quoi un drawdown en trading ?"</div></div>
<div class="chat-input"><input type="text" id="chatInput" placeholder="Pose ta question..." onkeypress="if(event.key==='Enter')poserQuestion()"><button onclick="poserQuestion()">Demander</button></div>
</div></div>
<script>
var NBQ = 5;
var sujet = 'ielts';
var quiz = [];
var qIdx = 0;
var score = 0;
var reponses = [];
var enCours = false;

function changerSujet(s){
    sujet=s;
    document.querySelectorAll('.tab').forEach(function(t){t.classList.remove('active')});
    document.getElementById('tab'+(s==='ielts'?'Ielts':s==='trading'?'Trading':'General')).classList.add('active');
    resetQuiz();
}

function resetQuiz(){
    quiz=[]; qIdx=0; score=0; reponses=[]; enCours=false;
    document.getElementById('question').textContent='Clique sur "Nouveau Quiz" pour commencer';
    document.getElementById('options').innerHTML='';
    document.getElementById('result').innerHTML='';
    document.getElementById('btnQuiz').textContent='🎲 Nouveau Quiz (5 questions)';
}

async function actionQuiz(){
    if(!enCours){
        document.getElementById('btnQuiz').textContent='⏳ Generation...';
        document.getElementById('btnQuiz').disabled=true;
        try{
            var r = await fetch('/api/quiz',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sujet:sujet})});
            var d = await r.json();
            if(d.error){alert(d.error);resetQuiz();return;}
            quiz=d.questions;
            qIdx=0; score=0; reponses=new Array(NBQ).fill(null); enCours=true;
            document.getElementById('btnQuiz').textContent='⏭ Question suivante';
            document.getElementById('btnQuiz').disabled=false;
            document.getElementById('result').innerHTML='';
            afficherQuestion(0);
        }catch(e){alert('Erreur reseau');resetQuiz();}
    }else{
        if(reponses[qIdx]===quiz[qIdx].bonne_reponse)score++;
        qIdx++;
        if(qIdx<NBQ){afficherQuestion(qIdx);}
        else{finQuiz();}
    }
}

function afficherQuestion(i){
    var q=quiz[i];
    document.getElementById('question').textContent='Question '+(i+1)+'/'+NBQ+' : '+q.question;
    var h=''; var lettres=['A','B','C','D'];
    q.options.forEach(function(o,j){
        h+='<div class="option'+(reponses[i]===j?' selected':'')+'" onclick="selectionner('+j+')" id="opt'+j+'">'+lettres[j]+'. '+o+'</div>';
    });
    document.getElementById('options').innerHTML=h;
    qIdx=i;
}

function selectionner(j){
    document.querySelectorAll('.option').forEach(function(o){o.classList.remove('selected')});
    document.getElementById('opt'+j).classList.add('selected');
    reponses[qIdx]=j;
}

function finQuiz(){
    if(reponses[qIdx]===quiz[qIdx].bonne_reponse)score++;
    enCours=false;
    var h='<div style="margin-top:15px;text-align:left">'; var err=0;
    for(var i=0;i<NBQ;i++){
        var q=quiz[i]; var ri=reponses[i]; var bon=q.bonne_reponse;
        if(ri!==bon){
            err++;
            h+='<div class="correction-box"><strong>❌ Q'+(i+1)+' : '+q.question+'</strong><br><span style="color:#e94560">Ta reponse : '+(q.options[ri]||'Pas repondu')+'</span><br><span style="color:#4ecca3">✅ Bonne reponse : '+q.options[bon]+'</span><span class="explanation">💡 '+(q.explication||'Revise ce sujet.')+'</span></div>';
        }
    }
    h+='</div>';
    if(err===0)h='<div style="color:#4ecca3;font-weight:bold;margin-top:10px">🌟 Parfait ! 5/5</div>';
    document.getElementById('question').textContent='Quiz termine !';
    document.getElementById('options').innerHTML=h;
    document.getElementById('btnQuiz').textContent='🎲 Nouveau Quiz (5 questions)';
    var cl=score>=8?'good':(score>=5?'ok':'bad');
    var msg=score>=8?'Excellent ! 🌟':(score>=5?'Pas mal !':'Entraine-toi encore !');
    document.getElementById('result').innerHTML='<div class="result '+cl+'">'+score+'/'+NBQ+' — '+msg+'</div>';
    fetch('/api/score',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({score:score,sujet:sujet})});
    chargerDashboard();
}

async function reinitialiserScores(){
    if(confirm('Reinitialiser tous les scores ?')){
        await fetch('/api/reinitialiser',{method:'POST'});
        resetQuiz();
        chargerDashboard();
    }
}

async function chargerDashboard(){
    try{
        var r=await fetch('/api/progres'); var d=await r.json();
        document.getElementById('quizPasses').textContent=d.quiz_passes;
        document.getElementById('moyenne').textContent=d.moyenne;
        document.getElementById('objectifIelts').textContent=d.objectif_ielts;
        document.getElementById('derniereSession').textContent=d.derniere_session||'Aucune';
        var pf=d.points_faibles||[];
        document.getElementById('pointsFaibles').textContent=pf.length>0?pf.join(', '):'—';
        if(d.historique&&d.historique.length>0){
            var derniers=d.historique.slice(-20); var h='';
            derniers.forEach(function(q){
                var ht=(q.score/NBQ)*70;
                var c=q.score>=8?'#4ecca3':(q.score>=5?'#f0a500':'#e94560');
                h+='<div style="min-width:22px;text-align:center" title="'+q.date+' - '+q.sujet+' : '+q.score+'/5"><div style="background:'+c+';height:'+ht+'px;border-radius:3px 3px 0 0"></div><span style="font-size:8px;color:#888">'+q.score+'</span></div>';
            });
            document.getElementById('evolution').innerHTML=h;
        }else{
            document.getElementById('evolution').innerHTML='<span style="color:#888;font-size:12px">Aucun quiz passe</span>';
        }
    }catch(e){}
}

async function poserQuestion(){
    var input=document.getElementById('chatInput');
    var q=input.value.trim();
    if(!q)return;
    var msg=document.getElementById('chatMessages');
    msg.innerHTML+='<div class="chat-msg user">'+q+'</div>';
    msg.innerHTML+='<div class="chat-msg agent loading-msg" id="loadMsg">📚 Recherche...</div>';
    msg.scrollTop=msg.scrollHeight;
    input.value='';
    try{
        var r=await fetch('/api/tuteur',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
        var d=await r.json();
        document.getElementById('loadMsg').remove();
        msg.innerHTML+='<div class="chat-msg agent">'+d.reponse.replace(/\\n/g,'<br>')+'</div>';
        msg.scrollTop=msg.scrollHeight;
    }catch(e){
        document.getElementById('loadMsg').remove();
        msg.innerHTML+='<div class="chat-msg agent">❌ Erreur de connexion.</div>';
    }
}

chargerDashboard();
</script>
</body>
</html>"""

# Sauvegarder le template dans un fichier
with open(TEMPLATE_PATH, 'w') as f:
    f.write(TEMPLATE_CONTENU)

# Lire le template
with open(TEMPLATE_PATH, 'r') as f:
    HTML_TEMPLATE = f.read()

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/api/progres')
def api_progres():
    return jsonify(charger_progres())

@app.route('/api/reinitialiser', methods=['POST'])
def api_reinitialiser():
    return jsonify(reinitialiser_progres())

@app.route('/api/quiz', methods=['POST'])
def api_quiz():
    sujet = request.json.get('sujet', 'ielts')
    prompts = {
    "ielts": "Genere un QCM de 5 questions en anglais pour l'IELTS (B2-C1). Chaque explication : 1 phrase courte en francais. Format JSON uniquement: [{\"question\":\"...\",\"options\":[\"A\",\"B\",\"C\",\"D\"],\"bonne_reponse\":0,\"explication\":\"...\"}]",
    "trading": "Genere un QCM de 5 questions sur le trading debutant. Chaque explication : 1 phrase courte en francais. Format JSON uniquement.",
    "general": "Genere un QCM de 5 questions de culture generale. Chaque explication : 1 phrase courte en francais. Format JSON uniquement."
}
    
    # On essaie jusqu'à 3 fois si le JSON est mal formé
    for tentative in range(3):
        try:
            response = ollama.chat(model="qwen2.5:7b", messages=[
                {"role": "system", "content": "Tu es un generateur de quiz. Reponds UNIQUEMENT avec un tableau JSON valide. Pas de texte avant ni apres. Pas de virgule apres le dernier element. Toutes les cles entre guillemets doubles. Les explications ne doivent pas contenir de guillemets doubles (utilise des guillemets simples ou des apostrophes a la place)."},
                {"role": "user", "content": prompts.get(sujet, prompts["ielts"])}
            ])
            contenu = response['message']['content'].strip()
            
            # Nettoyage agressif
            if contenu.startswith("```"):
                contenu = contenu.split("\n", 1)[1]
                if contenu.endswith("```"):
                    contenu = contenu.rsplit("\n", 1)[0]
            
            # Supprimer les virgules avant les crochets/accolades fermants
            import re
            contenu = re.sub(r',\s*]', ']', contenu)
            contenu = re.sub(r',\s*}', '}', contenu)
            
            questions = json.loads(contenu)
            return jsonify({"questions": questions})
            
        except Exception as e:
            if tentative == 2:
                return jsonify({"error": f"Echec apres 3 tentatives: {str(e)}"})
            # Sinon on réessaie
    
    return jsonify({"error": "Erreur inconnue"})

@app.route('/api/score', methods=['POST'])
def api_score():
    score = request.json.get('score', 0)
    sujet = request.json.get('sujet', 'ielts')
    return jsonify(enregistrer_quiz(score, sujet))

@app.route('/api/tuteur', methods=['POST'])
def api_tuteur():
    question = request.json.get('question', '')
    progres = charger_progres()
    try:
        response = ollama.chat(model="qwen2.5:7b", messages=[
            {"role": "system", "content": f"Tu es Learning AI, tuteur d'Isaie. Objectif IELTS: {progres['objectif_ielts']}. Quiz passes: {progres['quiz_passes']}. Moyenne: {progres['moyenne']}/5. Sois pedagogique, simple, encourageant. Reponds en 10-15 lignes max. Propose un exercice a la fin."},
            {"role": "user", "content": question}
        ])
        return jsonify({"reponse": response['message']['content'].strip()})
    except Exception as e:
        return jsonify({"reponse": f"Erreur: {e}"})

if __name__ == '__main__':
    reinitialiser_progres()
    print("📚 Learning AI - Tuteur IELTS & Culture G")
    print("http://127.0.0.1:5005")
    app.run(debug=True, host='127.0.0.1', port=5005)