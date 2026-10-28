#!/usr/bin/env python3
"""Render Myang (puppet.js spec) to PNGs for visual verification.
Grid: 6 expressions (neutral/unimused, smug, surprised=shock, angry=squint, happy=soft, sad) in poses,
plus stamp pose + evidence (glasses) variant. Outputs /home/z/my-project/download/myang/puppet_*.png
"""
import base64, functools, http.server, os, threading, json
from playwright.sync_api import sync_playwright

ENG = "/home/z/my-project/mega-shot/engine/core"
OUT = "/home/z/my-project/download/myang"
SPEC = json.load(open("/home/z/my-project/studio/.mega-shot/characters/myang.json"))
SPEC_EV = json.load(open("/home/z/my-project/studio/.mega-shot/characters/myang_evidence.json"))
del SPEC["_notes"], SPEC_EV["_notes"]

CELLS = [
    ("unimused (idle)",       "myang",    [{ "t": 0, "pose": "idle",   "expr": "unimused" }]),
    ("smug (point)",          "myang",    [{ "t": 0, "pose": "point",  "expr": "smug" }]),
    ("shock (surprised)",     "myang",    [{ "t": 0, "pose": "idle",   "expr": "surprised" }]),
    ("squint (suspicious)",   "myang",    [{ "t": 0, "pose": "arms-crossed", "expr": "angry" }]),
    ("soft smile (explain)",  "myang",    [{ "t": 0, "pose": "explain","expr": "happy" }]),
    ("shrug",                 "myang",    [{ "t": 0, "pose": "shrug",  "expr": "sad" }]),
    ("STAMP CEREMONY",        "myang",    [{ "t": 0, "pose": "stamp",  "expr": "neutral" }]),
    ("EVIDENCE (glasses)",    "myang_ev", [{ "t": 0, "pose": "explain","expr": "smug" }]),
]

PAGE = """<!doctype html><meta charset="utf-8"><canvas id="c" width="1080" height="2680"></canvas>
<script src="/util.js"></script><script src="/overlay.js"></script><script src="/puppet.js"></script>
<script>
const SPEC  = %s;
const SPEC_EV = %s;
MS.FMT = MS.FORMATS['9x16']; MS.LANG = 'en'; MS.STYLE = MS.STYLE || {}; MS.STYLE.font = 'Noto Sans SC, Arial';
const CH = { myang: MS.puppet.create(SPEC), myang_ev: MS.puppet.create(SPEC_EV) };
function drawCell(g, i, x0, y0) {
  const [label, ch, track] = CELLS[i];
  g.save(); g.translate(x0, y0);
  g.fillStyle = '#f7f2e6'; g.fillRect(0, 0, 520, 620);
  g.strokeStyle = '#d8cfb8'; g.lineWidth = 3; g.strokeRect(4, 4, 512, 612);
  MS.puppet.pen(0.9, i + 3, { boil: 0 });
  MS.puppet.draw(g, CH[ch], { x: 260, y: 470, scale: 1.05, t: 0.9, track, boil: 0 });
  g.fillStyle = '#2b2620'; g.font = '600 30px Arial'; g.textAlign = 'center'; g.fillText(label, 260, 585);
  g.restore();
}
function draw(t) {
  const c = document.getElementById('c'), g = c.getContext('2d');
  g.fillStyle = '#efe8d6'; g.fillRect(0, 0, 1080, 2680);
  window.CELLS.forEach((_, i) => drawCell(g, i, i %% 2 ? 548 : 12, 90 + Math.floor(i / 2) * 640));
  g.fillStyle = '#2b2620'; g.font = '700 52px Arial'; g.textAlign = 'center'; g.fillText('MYANG — spec v1 · 6 moods + stamp + evidence', 540, 55);
  g.fillStyle = '#6b6152'; g.font = '500 26px Arial'; g.fillText("cream plush · emerald accents · FILE \u2116 001 tag · brass stamp · gold glasses (evidence)", 540, 2655);
  return c.toDataURL('image/png');
}
window.CELLS = %s; window.draw = draw;
</script>""" % (json.dumps(SPEC), json.dumps(SPEC_EV), json.dumps(CELLS))

def main():
    os.makedirs(OUT, exist_ok=True)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(
        type("Q", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *x: None}), directory=ENG))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    page_html = os.path.join("/tmp", "myang_test.html"); open(page_html, "w").write(PAGE)
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1080, "height": 2680})
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        # serve the page from the same origin so /util.js etc resolve: copy into eng dir instead
        eng_page = os.path.join(ENG, "_myang_test.html"); open(eng_page, "w").write(PAGE)
        try:
            pg.goto(f"http://127.0.0.1:{srv.server_port}/_myang_test.html")
            pg.wait_for_function("window.draw && window.MS && MS.puppet")
            pg.wait_for_function("window.CELLS && window.CELLS.length === 8")
            data = pg.evaluate("draw(0)")
            p = os.path.join(OUT, "puppet_sheet.png")
            open(p, "wb").write(base64.b64decode(data.split(",", 1)[1]))
            print("OK ->", p)
        except Exception as e:
            print("FAILED:", e)
        finally:
            os.remove(eng_page); b.close()
        if errs: print("PAGE ERRORS:", errs)
    srv.shutdown()

if __name__ == "__main__":
    main()
