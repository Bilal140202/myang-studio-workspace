#!/usr/bin/env python3
"""Build the final SRT for the dolphins video.

Timing source: build/timeline_with_subs_backup.json — 48 verbatim caption lines whose
word times come from Edge-TTS WordBoundary data of the ACTUAL narration audio
(verified frame-level: 'ocean' lands 5.662 vs meta 5.675).
The z-ai ASR transcript (run separately on the final mix) cross-checks the words.
"""
import json

VID = "/home/z/my-project/studio/videos/dolphins"
OUT = "/home/z/my-project/download/dolphins-video/dolphins.en.srt"


def ts(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


tl = json.load(open(f"{VID}/build/timeline_with_subs_backup.json"))
subs = tl["subs"]
lines = []
for i, s in enumerate(subs, 1):
    lines.append(f"{i}\n{ts(s['t0'])} --> {ts(s['t1'])}\n{s['s']}\n")
open(OUT, "w").write("\n".join(lines))
print(f"SRT written: {OUT} ({len(subs)} cues, {subs[0]['t0']:.2f}s .. {subs[-1]['t1']:.2f}s)")

# also plain transcript for the ASR cross-check
words = " ".join(s["s"] for s in subs)
open(f"{VID}/out/subtitles/dolphins.en.txt", "w").write(words + "\n")
print("transcript words:", len(words.split()))
