#!/usr/bin/env python3
import urllib.request, json, websocket, time, argparse, sys, base64

parser = argparse.ArgumentParser()
parser.add_argument("--symbol", default="BTCUSD")
parser.add_argument("--tf",     default="15")
parser.add_argument("--port",   default="9222")
args = parser.parse_args()

pine_raw = open("scripts/fbo_strategy.pine", "r").read()
pine_b64 = base64.b64encode(pine_raw.encode("utf-8")).decode("ascii")

def get_tab(port):
    tabs = json.loads(urllib.request.urlopen(f"http://localhost:{port}/json").read())
    for t in tabs:
        if "tradingview" in t.get("url","").lower():
            return t
    return None

def js(ws, code, mid=1):
    ws.send(json.dumps({"id":mid,"method":"Runtime.evaluate",
                        "params":{"expression":code,"awaitPromise":True}}))
    return json.loads(ws.recv())

print(f"\n{'='*60}")
print(f"  FBO Injector — {args.symbol} TF:{args.tf}")
print(f"{'='*60}\n")

tab = get_tab(args.port)
if not tab:
    print("❌ TradingView non trouvé"); sys.exit(1)
print(f"[1] ✅ {tab['title']}")

ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=15)
print(f"[2] ✅ CDP connecté")

print(f"[3] ⏳ Injection...")
r = js(ws, f"""
(async () => {{
    const b64  = '{pine_b64}';
    const code = atob(b64);

    // Méthode 1 : Monaco inputarea (celle qui a marché)
    const monaco_ta = document.querySelector('.inputarea.monaco-mouse-cursor-text');
    if (monaco_ta) {{
        monaco_ta.focus();
        await new Promise(r=>setTimeout(r,400));
        monaco_ta.dispatchEvent(new KeyboardEvent('keydown',{{key:'a',ctrlKey:true,bubbles:true}}));
        await new Promise(r=>setTimeout(r,300));
        const ok = document.execCommand('insertText', false, code);
        if (ok) return 'SUCCESS Monaco inputarea execCommand';

        // Fallback nativeSetter
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
        setter.call(monaco_ta, code);
        monaco_ta.dispatchEvent(new Event('input',{{bubbles:true}}));
        monaco_ta.dispatchEvent(new Event('change',{{bubbles:true}}));
        return 'SUCCESS Monaco inputarea nativeSetter len=' + monaco_ta.value.length;
    }}

    // Méthode 2 : toutes les textareas visibles
    const all = [...document.querySelectorAll('textarea')];
    const visible = all.filter(t => {{
        const r = t.getBoundingClientRect();
        return r.width > 0 && r.height > 0;
    }});
    if (visible.length > 0) {{
        const ta = visible[0];
        ta.focus();
        await new Promise(r=>setTimeout(r,400));
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
        setter.call(ta, code);
        ta.dispatchEvent(new Event('input',{{bubbles:true}}));
        ta.dispatchEvent(new Event('change',{{bubbles:true}}));
        return 'SUCCESS visible textarea len=' + ta.value.length;
    }}

    // Debug
    const info = all.map(t=>{{
        const r=t.getBoundingClientRect();
        return t.className+' w='+Math.round(r.width)+' h='+Math.round(r.height);
    }});
    return 'ERROR: ' + JSON.stringify(info);
}})()
""", 2)

val = r.get('result',{}).get('result',{}).get('value','?')
print(f"[3] {val}")

if 'SUCCESS' in str(val):
    time.sleep(1)
    r2 = js(ws, """
(async()=>{
    await new Promise(r=>setTimeout(r,800));
    // Cherche bouton Add to chart
    let btn = document.querySelector('[data-name="add-script-to-chart"]');
    if(btn){ btn.click(); return 'OK data-name'; }
    const btns = [...document.querySelectorAll('button,[role=button]')];
    btn = btns.find(b=>b.textContent.match(/Add to chart|Ajouter/i));
    if(btn){ btn.click(); return 'OK: '+btn.textContent.trim(); }
    // Bouton play ▶
    const play = document.querySelector('[data-name="pine-editor-run-button"]');
    if(play){ play.click(); return 'OK play'; }
    return 'Manuel: clique ▶ dans Pine Editor. Boutons: '+btns.slice(0,5).map(b=>b.textContent.trim().substring(0,15)).join(' | ');
})()
""", 3)
    val2 = r2.get('result',{}).get('result',{}).get('value','?')
    print(f"[4] Add to chart : {val2}")
    print(f"\n✅ FBO injecté sur {args.symbol} !")
else:
    print(f"\n⚠️  Échec — clique dans Pine Editor puis relance")

ws.close()
print(f"{'='*60}\n")
