#!/bin/bash

echo "🧠 Démarrage d'ATLAS OS..."
echo ""

# Activation de l'environnement virtuel
source venv/bin/activate

# Dossier du projet
cd ~/Desktop/ATLAS-OS

# Lancement de chaque agent dans une nouvelle fenêtre de terminal
echo "📄 Lancement de Dupsolaz AI (port 5000)..."
osascript -e 'tell app "Terminal" to do script "cd ~/Desktop/ATLAS-OS && source venv/bin/activate && python 02-Dupsolaz-AI/app.py"'

sleep 1

echo "💰 Lancement de Finance AI (port 5001)..."
osascript -e 'tell app "Terminal" to do script "cd ~/Desktop/ATLAS-OS && source venv/bin/activate && python 03-Finance-AI/app.py"'

sleep 1

echo "🦘 Lancement de Australia AI (port 5002)..."
osascript -e 'tell app "Terminal" to do script "cd ~/Desktop/ATLAS-OS && source venv/bin/activate && python 05-Australia-AI/app.py"'

sleep 1

echo "🧠 Lancement de Chief AI (port 5003)..."
osascript -e 'tell app "Terminal" to do script "cd ~/Desktop/ATLAS-OS && source venv/bin/activate && python 01-Chief-AI/app.py"'

sleep 1

echo "📈 Lancement de Trading AI (port 5004)..."
osascript -e 'tell app "Terminal" to do script "cd ~/Desktop/ATLAS-OS && source venv/bin/activate && python 04-Trading-AI/app.py"'

sleep 1

echo "📚 Lancement de Learning AI (port 5005)..."
osascript -e 'tell app "Terminal" to do script "cd ~/Desktop/ATLAS-OS && source venv/bin/activate && python 06-Learning-AI/app.py"'

echo ""
echo "✅ ATLAS OS est lancé !"
echo ""
echo "📄 Dupsolaz AI  → http://127.0.0.1:5000"
echo "💰 Finance AI   → http://127.0.0.1:5001"
echo "🦘 Australia AI → http://127.0.0.1:5002"
echo "🧠 Chief AI     → http://127.0.0.1:5003"
echo "📈 Trading AI   → http://127.0.0.1:5004"
echo "📚 Learning AI  → http://127.0.0.1:5005"
echo ""
echo "⚠️  Laisse les fenêtres Terminal ouvertes."