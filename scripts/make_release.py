#!/usr/bin/env python3
"""Create a GitHub release on Bilal140202/myang-studio and upload deliverable assets.
Usage: GITHUB_TOKEN=ghp_... python3 scripts/make_release.py <tag> <title> <body-file> [asset:label ...]
"""
import json
import os
import sys
import urllib.request
import urllib.error

TOKEN = os.environ["GITHUB_TOKEN"]
REPO = "Bilal140202/myang-studio"
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


tag, title, body_file = sys.argv[1], sys.argv[2], sys.argv[3]
assets = []
for a in sys.argv[4:]:
    path, _, label = a.partition(":")
    assets.append((path, os.path.basename(path), label or None))

body = open(body_file).read()
rel = api("POST", f"{API}/repos/{REPO}/releases", json.dumps({
    "tag_name": tag,
    "target_commitish": "main",
    "name": title,
    "body": body,
}).encode())
print("release:", rel["html_url"])

for path, name, label in assets:
    with open(path, "rb") as f:
        data = f.read()
    url = f"{UPLOAD}/repos/{REPO}/releases/{rel['id']}/assets?name={name}"
    if label:
        url += "&label=" + urllib.request.quote(label)
    try:
        r = api("POST", url, data, "application/octet-stream")
        print("OK  {:36s} {:>9,} bytes".format(name, r["size"]))
    except urllib.error.HTTPError as e:
        print("FAIL {}: {} {}".format(name, e.code, e.read().decode()[:200]))
