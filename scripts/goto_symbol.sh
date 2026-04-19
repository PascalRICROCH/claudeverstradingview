#!/bin/bash
SYMBOL=${1:-XAUUSD}
echo "Navigation vers $SYMBOL..."

python3 - << PYEOF
import urllib.request, json, websocket, time

tabs = json.loads(urllib.request.urlopen('http://localhost:9222/json').read())
ws_url = None
for tab in tabs:
    if 'tradingview' in tab.get('url', '').lower():
        ws_url = tab['webSocketDebuggerUrl']
        break

if not ws_url:
    print("TradingView non trouvé")
    exit(1)

ws = websocket.create_connection(ws_url, timeout=10)
ws.send(json.dumps({
    "id": 1,
    "method": "Page.navigate",
    "params": {"url": f"https://www.tradingview.com/chart/?symbol=$SYMBOL"}
}))
time.sleep(2)
ws.recv()
ws.close()
print("$SYMBOL ouvert !")
PYEOF
