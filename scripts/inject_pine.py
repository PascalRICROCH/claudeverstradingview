#!/usr/bin/env python3
import urllib.request, json, websocket, time, argparse, sys, base64

parser = argparse.ArgumentParser()
parser.add_argument("--symbol", default="XAUUSD")
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
time.sleep(1)

# Injecte via l'API Monaco Editor
print(f"[3] ⏳ Injection via Monaco Editor...")
r = js(ws, f"""
(async () => {{
    const b64  = '{pine_b64}';
    const code = atob(b64);

    // Méthode 1 : API Monaco globale
    if (typeof monaco !== 'undefined') {{
        const models = monaco.editor.getModels();
        if (models.length > 0) {{
            models[0].setValue(code);
            return 'SUCCESS Monaco API models=' + models.length;
        }}
        const editors = monaco.editor.getEditors();
        if (editors.length > 0) {{
            editors[0].setValue(code);
            return 'SUCCESS Monaco getEditors len=' + editors.length;
        }}
    }}

    // Méthode 2 : via l'instance Monaco attachée au DOM
    const monacoEl = document.querySelector('.monaco-editor');
    if (monacoEl) {{
        // Cherche l'instance via la propriété _modelData ou similar
        const keys = Object.keys(monacoEl).filter(k => k.startsWith('__'));
        for (const k of keys) {{
            const inst = monacoEl[k];
            if (inst && inst._modelData && inst._modelData.model) {{
                inst._modelData.model.setValue(code);
                return 'SUCCESS via __key modelData';
            }}
            if (inst && typeof inst.setValue === 'function') {{
                inst.setValue(code);
                return 'SUCCESS via __key setValue';
            }}
        }}
    }}

    // Méthode 3 : clipboard + Ctrl+A + Ctrl+V sur Monaco textarea
    const ta = document.querySelector('.inputarea.monaco-mouse-cursor-text');
    if (ta) {{
        ta.focus();
        await new Promise(r => setTimeout(r, 300));

        // Ctrl+A pour tout sélectionner
        ta.dispatchEvent(new KeyboardEvent('keydown', {{
            key: 'a', code: 'KeyA', ctrlKey: true, bubbles: true, cancelable: true
        }}));
        await new Promise(r => setTimeout(r, 200));

        // Insère via execCommand
        const result = document.execCommand('insertText', false, code);
        if (result) return 'SUCCESS execCommand Monaco textarea';

        // Fallback : input event
        const nativeSetter = Object.getOwnPropertyDescriptor(
            window.HTMLTextAreaElement.prototype, 'value').set;
        nativeSetter.call(ta, code);
        ta.dispatchEvent(new InputEvent('input', {{bubbles: true, data: code}});
        return 'SUCCESS nativeSetter Monaco textarea len=' + ta.value.length;
    }}

    return 'ERROR: Monaco non trouvé. monaco=' + (typeof monaco);
}})()
""", 2)

val = r.get('result',{}).get('result',{}).get('value','?')
print(f"[3] Injection : {val}")

if 'SUCCESS' in str(val):
    time.sleep(1)
    # Clique Add to chart
    r2 = js(ws, """
(async () => {
    await new Promise(r => setTimeout(r, 500));

    // Cherche le bouton Add to chart / play
    let btn = document.querySelector('[data-name="add-script-to-chart"]');
    if (btn) { btn.click(); return 'OK data-name'; }

    const btns = [...document.querySelectorAll('button,[role=button]')];
    btn = btns.find(b =>
        b.textContent.match(/Add to chart|Ajouter au graphique/i) ||
        b.getAttribute('aria-label')?.match(/add to chart|ajouter/i)
    );
    if (btn) { btn.click(); return 'OK: ' + btn.textContent.trim(); }

    // Raccourci Ctrl+Enter dans Monaco
    const ta = document.querySelector('.inputarea.monaco-mouse-cursor-text');
    if (ta) {
        ta.dispatchEvent(new KeyboardEvent('keydown', {
            key: 'Enter', ctrlKey: true, bubbles: true
        }));
        return 'OK Ctrl+Enter';
    }

    return 'boutons: ' + btns.slice(0,8).map(b=>b.textContent.trim().substring(0,20)).join(' | ');
})()
""", 3)
    val2 = r2.get('result',{}).get('result',{}).get('value','?')
    print(f"[4] Add to chart : {val2}")
    print(f"\n✅ FBO injecté sur {args.symbol} TF:{args.tf} !")
else:
    print(f"\n⚠️  {val}")
    print("    Pine Editor est bien ouvert et visible ?")

ws.close()
print(f"{'='*60}\n")
