#!/usr/bin/env python3
"""Parallel batch-fetch CC images for the procrastination series via imgagent.
Resumable (per-query cache in _imgpool/manifest.json). Licenses -> _imgpool/licenses.json.
Query fallback chain: full -> first 2 words -> first word.
Run from series root: python3 fetch_images.py [top_per_query] [workers]
"""
import json, os, shutil, subprocess, sys, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from kichban_master import TEASER, EPISODES

TOP = int(sys.argv[1]) if len(sys.argv) > 1 else 3
WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 6
POOL = os.path.join(ROOT, "_imgpool")
PROJ = "proc"
MANIFEST = os.path.join(POOL, "manifest.json")
LIC = os.path.join(POOL, "licenses.json")
os.makedirs(POOL, exist_ok=True)

queries = []
for ep in EPISODES:
    for s in ep["scenes"]:
        for q in s["queries"]:
            if q not in queries: queries.append(q)
for s in TEASER["scenes"]:
    for q in s["queries"]:
        if q not in queries: queries.append(q)

manifest = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
licenses = json.load(open(LIC)) if os.path.exists(LIC) else {}

def slug(q, i):
    h = hashlib.md5(q.encode()).hexdigest()[:6]
    words = "".join(c if c.isalnum() else "-" for c in q.lower())[:40].strip("-")
    return f"{words}-{h}-{i:02d}.jpg"

def extract(data):
    cands = {c["candidate_id"]: c for c in data.get("candidates") or []}
    picks = []
    for dr in data.get("download_results") or []:
        p = dr.get("path")
        c = cands.get(dr.get("candidate_id"), {})
        if not p or not os.path.exists(p): continue
        try: w, h = Image.open(p).size
        except Exception: continue
        if w < 700: continue
        picks.append(dict(path=p, w=w, h=h,
                          author=c.get("creator") or "unknown",
                          license=c.get("license_name") or "CC (see source)",
                          page=c.get("source_page_url") or "",
                          title=c.get("title") or "",
                          provider=c.get("provider") or ""))
    return picks

def run_query(qraw):
    variants = [qraw, " ".join(qraw.split()[:2]), qraw.split()[0]]
    seen = set()
    for q in variants:
        if q in seen: continue
        seen.add(q)
        try:
            r = subprocess.run(["imgagent", "run", q, "--limit", "10", "--top", "5",
                                "--out", POOL, "--project", PROJ, "--json"],
                               capture_output=True, text=True, timeout=240, cwd=ROOT)
            out = r.stdout[r.stdout.find("{"):]
            picks = extract(json.loads(out)["data"])
            if picks:
                return qraw, picks, None, q
        except Exception:
            continue
    return qraw, [], "all variants empty", qraw

todo = [q for q in queries if q not in manifest or len(manifest[q]["files"]) < TOP]
print(f"{len(queries)} queries ({len(todo)} to fetch), top {TOP}, {WORKERS} workers")
fail = 0
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = {ex.submit(run_query, q): q for q in todo}
    for n, fut in enumerate(as_completed(futs), 1):
        q, picks, err, used = fut.result()
        if err:
            print(f"[{n}] FAIL {q}: {err}"); fail += 1; continue
        picks.sort(key=lambda p: -(p["w"] / p["h"] if p["h"] else 0) * min(p["w"], 3000))
        files = []
        for i, p in enumerate(picks[:TOP], 1):
            dst = os.path.join(POOL, slug(used, i))
            shutil.copy(p["path"], dst)
            licenses[os.path.basename(dst)] = {k: p[k] for k in
                ("author", "license", "page", "title", "provider", "w", "h")}
            licenses[os.path.basename(dst)]["query"] = used
            files.append(os.path.basename(dst))
        manifest[q] = {"files": files, "used_variant": used}
        json.dump(manifest, open(MANIFEST, "w"), indent=1)
        json.dump(licenses, open(LIC, "w"), indent=1, ensure_ascii=False)
        print(f"[{n}] OK   {q} -> {len(files)}" + (f" (variant: {used})" if used != q else ""))

total = sum(len(v["files"]) for v in manifest.values())
print(f"DONE queries={len(queries)} fail={fail} files={total}")
