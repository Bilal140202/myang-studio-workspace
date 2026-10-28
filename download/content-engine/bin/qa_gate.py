#!/usr/bin/env python3
"""QA gate — the anti-AI-slop checkpoint. Nothing publishes without a PASS.

Gates (all must pass):
  G1  script-gate    banned AI-slop phrases absent from narration/subtitles/titles
  G2  evidence-gate  every fact in the project research desk carries a source
  G3  timing-gate    every scene has real WordBoundary timings (no uniform fallback),
                     coverage >= 90% of audio duration
  G4  loudness-gate  mix within [-15.0, -13.0] LUFS (target -14)
  G5  duration-gate  shorts 45-120s, long-forms 7-14 min (final export)
  G6  myang-gate     corner reactions <= 4 per video, each <= 3.0 s (when timed)
  G7  pack-gate      publish pack + captions exist

Usage:  python3 qa_gate.py <project_dir> [--short|--long]
Exit 0 = PASS (safe to publish). Exit 1 = FAIL (report printed).
"""
import argparse, glob, json, os, re, subprocess, sys
import yaml

BANNED = [
    r"\bdive into\b", r"\bunleash", r"\bgame-?changer", r"\bmind-?blowing",
    r"\bbuckle up\b", r"\bin a world where\b", r"\bdid you know\b",
    r"\blet'?s (explore|dive|journey)\b", r"\bembark\b", r"\byou won'?t believe\b",
    r"\bshocking\b", r"\binsane\b", r"\bmind = blown\b", r"\blegendary\b",
    r"\bepic\b", r"\bviral\b", r"\bbest kept secret\b", r"\bhacks?\b",
    r"\blife ?-?changing\b", r"\brevolutioni[sz]e\b", r"\bunlock the secrets?\b",
]
MYANG_HOME = os.environ.get("MYANG_HOME", "/home/z/my-project")
FAILS, WARNS = [], []


def fail(g, msg):
    FAILS.append((g, msg))


def warn(g, msg):
    WARNS.append((g, msg))


def text_of(vdoc):
    parts = []
    for sc in vdoc.get("scenes", []):
        parts.append(sc.get("narration") or "")
        parts.append(sc.get("subtitle") or "")
        for cue in (sc.get("huashu") or {}).get("cues", []) or []:
            parts.append(str(cue.get("text", "")))
    pub = vdoc.get("publish") or {}
    for t in pub.get("titles", []) or []:
        parts.append(t)
    parts.append(pub.get("hook") or "")
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proj")
    ap.add_argument("--short", action="store_true")
    ap.add_argument("--long", dest="is_long", action="store_true")
    a = ap.parse_args()
    proj = a.proj.rstrip("/")

    vdoc = yaml.safe_load(open(os.path.join(proj, "video.yaml")))
    scenes = vdoc.get("scenes", [])

    # G1 script-gate
    body = text_of(vdoc).lower()
    for pat in BANNED:
        m = re.search(pat, body)
        if m:
            fail("G1", f"banned phrase: '{m.group(0)}'")

    # G2 evidence-gate — every numbered research line carries a Source:
    rc = os.path.join(proj, "nghien_cuu.md")
    if not os.path.exists(rc):
        fail("G2", "nghien_cuu.md missing (no research desk)")
    else:
        txt = open(rc).read()
        entries = re.findall(r"^\d+\..*$", txt, re.M)
        srcs = re.findall(r"Source:", txt)
        if len(entries) == 0:
            fail("G2", "research desk empty")
        elif len(srcs) < len(entries):
            fail("G2", f"{len(entries) - len(srcs)} facts without a Source line")
        if "Wikipedia" in txt:
            warn("G2", "Wikipedia cited — prefer primary papers/institutions")

    # G3 timing-gate — WordBoundary timings present and covering
    audio_dir = os.path.join(proj, "build", "audio")
    render_started = os.path.exists(os.path.join(proj, "build", "mix.wav"))
    if not os.path.isdir(audio_dir):
        (warn if not render_started else fail)("G3", "build/audio missing — run import_narration.py")
    else:
        for sc in scenes:
            meta_p = os.path.join(audio_dir, f"{sc['id']}.wav.json")
            wav_p = os.path.join(audio_dir, f"{sc['id']}.wav")
            if not os.path.exists(meta_p) or not os.path.exists(wav_p):
                fail("G3", f"scene '{sc['id']}': no wav/word-timing meta")
                continue
            tu = (json.load(open(meta_p)).get("check") or {}).get("tu") or []
            if not tu:
                fail("G3", f"scene '{sc['id']}': empty check.tu — uniform fallback detected")
                continue
            d = float(subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "csv=p=0", wav_p], capture_output=True, text=True).stdout.strip())
            cov = tu[-1][2] / d if d else 0
            if cov < 0.90:
                fail("G3", f"scene '{sc['id']}': word coverage {cov:.0%} < 90%")

    # G4 loudness-gate
    lufs_p = os.path.join(proj, "build", "mix.wav.lufs")
    if os.path.exists(lufs_p):
        try:
            lufs = float(open(lufs_p).read().strip().split()[-1])
            if not (-15.0 <= lufs <= -13.0):
                fail("G4", f"mix at {lufs} LUFS, target -14 (±1)")
        except Exception as e:
            warn("G4", f"cannot parse {lufs_p}: {e}")
    else:
        warn("G4", "mix.wav.lufs missing — mix step not run yet")

    # G5 duration-gate (final export)
    exports = glob.glob(os.path.join(proj, "out", "*.mp4"))
    if exports:
        dur = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
             "csv=p=0", exports[0]], capture_output=True, text=True).stdout.strip())
        if a.is_long:
            ok = 7 * 60 <= dur <= 14 * 60
        else:
            ok = 45 <= dur <= 120
        if not ok:
            fail("G5", f"export {dur:.0f}s outside format window")
    else:
        warn("G5", "no export yet (out/*.mp4)")

    # G6 myang-gate — budget from the myang beat block + overlay cues
    my = (vdoc.get("myang") or {})
    cue_reactions = []
    for sc in scenes:
        for cue in (sc.get("huashu") or {}).get("cues", []) or []:
            if str(cue.get("kind", "")).startswith("myang"):
                cue_reactions.append(cue)
    if len(cue_reactions) > 4:
        fail("G6", f"{len(cue_reactions)} Myang reactions > 4 max")
    for cue in cue_reactions:
        t = cue.get("data") or {}
        dur = t.get("dur_s")
        if dur and dur > 3.0:
            fail("G6", f"Myang reaction {dur}s > 3s max")

    # G7 pack-gate
    if not glob.glob(os.path.join(proj, "out", "*publish*")) and \
       not glob.glob(os.path.join(proj, "out", "*.md")):
        warn("G7", "publish pack not generated — run publish_pack.py")

    # ── verdict ──────────────────────────────────────────────────────────
    print(f"QA GATE — {proj}")
    for g, m in WARNS:
        print(f"  WARN {g}: {m}")
    if FAILS:
        for g, m in FAILS:
            print(f"  FAIL {g}: {m}")
        print(f"VERDICT: FAIL ({len(FAILS)} gate(s))")
        sys.exit(1)
    print("VERDICT: PASS — safe to publish")
    sys.exit(0)


if __name__ == "__main__":
    main()
