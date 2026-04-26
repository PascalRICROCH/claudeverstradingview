# CLAUDE.md — FBO Trading Automation
## Projet : claudeverstradingview
## Auteur : PascalRICROCH
## GitHub : https://github.com/PascalRICROCH/claudeverstradingview

---

## CONTEXTE
Ce projet automatise l'injection du script Pine Script FBO (Flux + Block Order + Fibonacci)
dans TradingView via Chrome DevTools Protocol (CDP) sur Mac.

---

## STACK
- Python 3.9+
- Chrome CDP port 9222
- Pine Script v5
- Git / GitHub

---

## COMMANDES DISPONIBLES

### Lancer TradingView
```bash
./scripts/launch_tv_debug_mac.sh
```

### Naviguer vers un symbole
```bash
./scripts/goto_symbol.sh XAUUSD
./scripts/goto_symbol.sh BTCUSD
```

### Injecter le script FBO
```bash
python3 scripts/inject_pine.py --symbol XAUUSD --tf 15
python3 scripts/inject_pine.py --symbol BTCUSD --tf 15
```

### Tout en une commande
```bash
./scripts/launch_tv_debug_mac.sh && sleep 6 && ./scripts/goto_symbol.sh XAUUSD && sleep 5 && python3 scripts/inject_pine.py --symbol XAUUSD --tf 15
```

### Sauvegarder sur GitHub
```bash
git add . && git commit -m "message" && git push origin main
```

---

## STRUCTURE DES FICHIERS
```
claudeverstradingview/
├── CLAUDE.md                    ← ce fichier
├── package.json
├── rules.json                   ← règles de la stratégie FBO
├── scripts/
│   ├── fbo_strategy.pine        ← script Pine FBO complet
│   ├── inject_pine.py           ← injecteur CDP Python
│   ├── launch_tv_debug_mac.sh   ← lance Chrome avec CDP
│   ├── goto_symbol.sh           ← navigue vers un symbole
│   ├── open_gold.sh
│   └── open_gold_cdp.sh
```

---

## STRATÉGIE FBO

### Définition
FBO = Flux + Block Order + Fibonacci

### Règles d'entrée
1. **F — Flux** : tendance confirmée par EMA20 > EMA50 > EMA200 (bull) ou inverse (bear)
2. **B — Order Block** : dernier corps rouge avant impulsion verte (bull OB) ou vert avant rouge (bear OB)
3. **O — Fibonacci** : l'OB doit être dans la zone 0.618-0.786 du retracement

### Paramètres
- Pip Gold (XAUUSD) : $10/pip
- Pip BTC (BTCUSD) : $0.10/pip
- Profil conservateur : 1% du capital
- Profil modéré : 2% du capital
- Profil agressif : 5% du capital
- R:R tendance : 1:2
- R:R contre-tendance : 1:1.5

### Placement SL/TP
- **Long tendance** : entrée = haut OB, SL = bas OB - 0.05%, TP = entrée + risque × 2
- **Short tendance** : entrée = bas OB, SL = haut OB + 0.05%, TP = entrée - risque × 2
- **Long CT** : même règle mais SL élargi à 0.20%, RR 1:1.5
- **Short CT** : même règle mais SL élargi à 0.20%, RR 1:1.5

---

## TÂCHES AUTOMATISABLES PAR CLAUDE CODE

Quand l'utilisateur dit :

| Instruction | Action |
|-------------|--------|
| "Lance TradingView" | `./scripts/launch_tv_debug_mac.sh` |
| "Ouvre le Gold" | `./scripts/goto_symbol.sh XAUUSD` + inject |
| "Ouvre le BTC" | `./scripts/goto_symbol.sh BTCUSD` + inject |
| "Injecte le script" | `python3 scripts/inject_pine.py` |
| "Mets à jour Pine" | modifier `scripts/fbo_strategy.pine` + pbcopy |
| "Sauvegarde" | `git add . && git commit && git push` |
| "Lance tout" | launch + goto + inject en séquence |
| "Change le timeframe" | inject avec `--tf X` |
| "Optimise le script" | modifier `fbo_strategy.pine` + re-injecter |

---

## WORKFLOW QUOTIDIEN

```bash
# Matin — démarrage complet
./scripts/launch_tv_debug_mac.sh
sleep 6
# Ouvrir Pine Editor dans Chrome manuellement
python3 scripts/inject_pine.py --symbol XAUUSD --tf 15
# Cmd+A → Cmd+V → Cmd+Entrée dans Pine Editor

# Changer de symbole
./scripts/goto_symbol.sh BTCUSD
python3 scripts/inject_pine.py --symbol BTCUSD --tf 15
```

---

## NOTES IMPORTANTES
- Chrome doit être lancé avec `--remote-debugging-port=9222 --remote-allow-origins=*`
- Pine Editor doit être ouvert manuellement avant l'injection
- Après injection : Cmd+A → Cmd+V → Cmd+Entrée dans Pine Editor
- Le profil Chrome réel est utilisé pour conserver la session TradingView
- Ne jamais partager les tokens GitHub ou mots de passe

---

## RÉSULTATS VALIDÉS
- 19/04/2026 : BTC buy 8.96 lots @ 75,015 → 75,927 = **+$8,174** ✅
