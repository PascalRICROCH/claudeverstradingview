#!/bin/bash
echo "Lancement de Chrome avec debug CDP sur port 9222..."

pkill -9 "Google Chrome" 2>/dev/null
sleep 2

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir=/tmp/chrome-tv-debug \
  --no-first-run \
  --no-default-browser-check \
  "https://www.tradingview.com/chart/?symbol=XAUUSD" &

echo "Chrome lancé — TradingView XAUUSD en cours de chargement..."
