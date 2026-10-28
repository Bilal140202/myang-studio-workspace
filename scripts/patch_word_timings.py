#!/usr/bin/env python3
"""Patch mega-shot narration meta (build/audio/<id>.wav.json) with Edge-TTS word boundaries.
check.tu = [[word, start, end], ...] — seconds relative to the audio file start (same format
VoiceStudio's Whisper listen-back would produce). Then `xp timeline` anchors subtitles & cues on them.
"""
import json, os, subprocess, sys

VID = "/home/z/my-project/studio/videos/dolphins"
IDS = ["hook", "problem", "trick", "eye", "resting", "calf", "outro"]

for k, sid in enumerate(IDS):
    words_js = os.path.join(VID, "narration_edge", f"seg{k+1}.json")
    meta = os.path.join(VID, "build", "audio", f"{sid}.wav.json")
    words = json.load(open(words_js))["words"]
    wav = os.path.join(VID, "build", "audio", f"{sid}.wav")
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "csv=p=0", wav], capture_output=True, text=True).stdout.strip())
    last_end = words[-1]["end"] if words else 0
    assert last_end <= d + 0.05, f"{sid}: word timing {last_end:.2f}s exceeds audio {d:.2f}s"
    m = json.load(open(meta)) if os.path.exists(meta) else {}
    m.setdefault("check", {})
    m["check"]["id"] = sid
    m["check"]["dur"] = round(d, 2)
    m["check"]["tu"] = [[w["word"], w["start"], w["end"]] for w in words]
    json.dump(m, open(meta, "w"), ensure_ascii=False, indent=1)
    print(f"{sid:8s} {d:6.2f}s  {len(words):2d} words  last word ends {last_end:.2f}s")
print("OK — meta patched; next: xp timeline")
