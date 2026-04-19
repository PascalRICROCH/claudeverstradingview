#!/bin/bash
echo "Ouverture XAUUSD via CDP..."

# Récupère l'ID de l'onglet TradingView
TAB_ID=$(curl -s http://localhost:9222/json | python3 -c "
import sys, json
tabs = json.load(sys.stdin)
for tab in tabs:
    if 'tradingview' in tab.get('url', '').lower():
        print(tab['id'])
        break
")

echo "Onglet TradingView : $TAB_ID"

# Navigue vers XAUUSD
curl -s -X POST "http://localhost:9222/json/activate/$TAB_ID"

# Utilise CDP pour naviguer
python3 << PYEOF
import json, websocket, time

# Récupère le webSocket de l'onglet
import urllib.request
tabs = json.loads(urllib.request.urlopen('http://localhost:9222/json').read())
ws_url = None
for tab in tabs:
    if 'tradingview' in tab.get('url', '').lower():
        ws_url = tab['webSocketDebuggerUrl']
        break

if not ws_url:
    print("Onglet TradingView non trouvé")
    exit(1)

print(f"Connexion à : {ws_url}")
ws = websocket.create_connection(ws_url)

# Navigation vers XAUUSD
cmd = json.dumps({
    "id": 1,
    "method": "Page.navigate",
    "params": {"url": "https://www.tradingview.com/chart/?symbol=XAUUSD"}
})
ws.send(cmd)
result = ws.recv()
print(f"Résultat : {result}")
time.sleep(2)
ws.close()
print("XAUUSD ouvert !")
PYEOF
