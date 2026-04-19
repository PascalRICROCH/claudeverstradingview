#!/bin/bash
# Ouvre XAUUSD sur TradingView via CDP
echo "Ouverture Gold (XAUUSD) sur TradingView..."

curl -s http://localhost:9222/json | python3 -c "
import sys, json
tabs = json.load(sys.stdin)
for tab in tabs:
    if 'tradingview' in tab.get('url', '').lower():
        print(tab['id'])
        break
" | xargs -I {} curl -s -X POST \
  "http://localhost:9222/json/activate/{}" > /dev/null

open "http://localhost:9222" 2>/dev/null

# Navigation directe vers XAUUSD
osascript << 'APPLESCRIPT'
tell application "Google Chrome"
    set theUrl to "https://www.tradingview.com/chart/?symbol=XAUUSD"
    repeat with w in windows
        repeat with t in tabs of w
            if URL of t contains "tradingview" then
                set URL of t to theUrl
                return
            end if
        end repeat
    end repeat
end tell
APPLESCRIPT

echo "Gold (XAUUSD) ouvert !"
