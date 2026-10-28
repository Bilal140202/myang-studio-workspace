#!/usr/bin/env python3
"""Create GitHub release v1.0.0 for ansaribilal14/myang-studio and upload deliverable assets."""
import json
import os
import urllib.request
import urllib.error

# Never hardcode tokens. Export GITHUB_TOKEN before running.
TOKEN = os.environ["GITHUB_TOKEN"]
REPO = "ansaribilal14/myang-studio"
API = "https://api.github.com"
UPLOAD = "https://uploads.github.com"


def api(method, url, data=None, ctype="application/json"):
    req = urllib.request.Request(url, method=method, data=data)
    req.add_header("Authorization", "token " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    if ctype:
        req.add_header("Content-Type", ctype)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


BODY = """**Day 1 pilot shipped** — first production run of the full anti-slop pipeline.

## The video
| | |
|---|---|
| Title | How do dolphins sleep without drowning? |
| Master | `dolphins_9x16.mp4` — 79s · 1080x1920 (9:16) · H.264/AAC · **-14.0 LUFS** |
| Narration | en-GB-SoniaNeural (Edge TTS) · subtitles word-locked via WordBoundary timestamps |
| QA | Gates G1-G7 PASS · 8 sourced facts (WDC, Lyamin et al.) · zero banned phrases |

## Assets
- `dolphins_9x16.mp4` — final master
- `dolphins.en.srt` — word-timed subtitles
- `thumbnail.jpg` — YouTube cover
- `youtube-publish-pack.md` — title / description / tags
- `social-captions.md` — IG / TikTok / Shorts copy
- `30-day-content-calendar.xlsx` — 4 sheets (Calendar / Topic Bank / Long-forms / Production)
- `content-engine-playbook.docx` — full system manual incl. Myang spec
- `myang-mascot-kit.zip` — brand + puppet sheets, 7 expressions (PNG/SVG)

## Also in this repo
mega-shot engine (vendored, MIT) · content-engine `bin/` chain with QA gates G1-G7 · day-2 scaffold (`tardigrade-space`) already word-timed.

**Delivery policy:** from this release on, all files and final videos ship via GitHub Releases (see `DELIVERY.md`).
"""

rel = api("POST", API + "/repos/" + REPO + "/releases", json.dumps({
    "tag_name": "v1.0.0",
    "target_commitish": "main",
    "name": "v1.0.0 — Dolphins pilot (day 1) + 30-day engine + Myang mascot kit",
    "body": BODY,
}).encode())
print("release:", rel["html_url"], "id:", rel["id"])

ASSETS = [
    ("/home/z/my-project/download/dolphins-video/dolphins_9x16.mp4", "dolphins_9x16.mp4", "video/mp4"),
    ("/home/z/my-project/download/dolphins-video/dolphins.en.srt", "dolphins.en.srt", "application/octet-stream"),
    ("/home/z/my-project/download/dolphins-video/thumbnail.jpg", "thumbnail.jpg", "image/jpeg"),
    ("/home/z/my-project/download/dolphins-video/youtube-publish-pack.md", "youtube-publish-pack.md", "text/markdown"),
    ("/home/z/my-project/download/dolphins-video/social-captions.md", "social-captions.md", "text/markdown"),
    ("/home/z/my-project/download/content-engine/30-day-content-calendar.xlsx", "30-day-content-calendar.xlsx", "application/octet-stream"),
    ("/home/z/my-project/download/content-engine/content-engine-playbook.docx", "content-engine-playbook.docx", "application/octet-stream"),
    ("/home/z/my-project/download/myang-mascot-kit.zip", "myang-mascot-kit.zip", "application/zip"),
]

for path, name, ctype in ASSETS:
    with open(path, "rb") as f:
        data = f.read()
    url = "{}/repos/{}/releases/{}/assets?name={}".format(UPLOAD, REPO, rel["id"], name)
    try:
        r = api("POST", url, data, ctype)
        print("OK  {:34s} {:>9,} bytes  state={}".format(name, r["size"], r["state"]))
    except urllib.error.HTTPError as e:
        print("FAIL {}: {} {}".format(name, e.code, e.read().decode()[:300]))
