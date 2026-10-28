#!/usr/bin/env python3
"""Import Edge-TTS narration into mega-shot with real word timings.

Bypasses `xp narrate --import-from` (which stalls waiting for a VoiceStudio
ping in this environment). Instead:
  1. cp  narration_edge/seg<i>.wav -> build/audio/<scene_id>.wav
  2. patch build/audio/<scene_id>.wav.json  check.tu = [[word, start, end], ...]
  3. run `xp timeline` so subtitles + at_word cues anchor on spoken words

Usage:  python3 import_narration.py <project_dir>
"""
import json, os, shutil, subprocess, sys
import yaml

STUDIO = os.environ.get("MYANG_STUDIO", "/home/z/my-project/studio")


def ffprobe_dur(path):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True).stdout.strip())


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: import_narration.py <project_dir>")
    proj = sys.argv[1]
    vdoc = yaml.safe_load(open(os.path.join(proj, "video.yaml")))
    ndir = os.path.join(proj, "narration_edge")
    idx_path = os.path.join(ndir, "index.yaml")
    if not os.path.exists(idx_path):
        sys.exit("no narration_edge/index.yaml — run gen_narration.py first")
    index = {e["scene"]: e for e in yaml.safe_load(open(idx_path))}

    audio_dir = os.path.join(proj, "build", "audio")
    os.makedirs(audio_dir, exist_ok=True)

    for scene in vdoc["scenes"]:
        sid = scene["id"]
        e = index.get(sid)
        if not e:
            sys.exit(f"scene '{sid}' missing from narration index — re-run gen_narration.py")
        wav = os.path.join(audio_dir, f"{sid}.wav")
        shutil.copyfile(e["wav"], wav)
        words = json.load(open(e["json"]))["words"]
        d = ffprobe_dur(wav)
        last = words[-1]["end"] if words else 0.0
        assert last <= d + 0.05, f"{sid}: last word {last:.2f}s exceeds audio {d:.2f}s"
        meta_path = os.path.join(audio_dir, f"{sid}.wav.json")
        m = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
        m.setdefault("check", {})
        m["check"]["id"] = sid
        m["check"]["dur"] = round(d, 2)
        m["check"]["tu"] = [[w["word"], w["start"], w["end"]] for w in words]
        json.dump(m, open(meta_path, "w"), ensure_ascii=False, indent=1)
        print(f"{sid:<12} {d:6.2f}s  {len(words):2d} words")

    rc = subprocess.call(["bash", os.path.join(os.environ.get("MYANG_MEGASHOT",
                          "/home/z/my-project/mega-shot"), "xp"),
                          "timeline"], cwd=proj if os.path.isdir(proj) else STUDIO)
    print("xp timeline rc =", rc, "(rc!=0 in sandbox: long jobs get SIGKILLed — re-run; caches make it cheap)")
    print("OK — next: bin/render.sh", proj)


if __name__ == "__main__":
    main()
