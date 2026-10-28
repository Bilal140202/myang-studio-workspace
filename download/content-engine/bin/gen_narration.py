#!/usr/bin/env python3
"""Narration generator — Edge TTS with word-level timestamps.

Reads every scene's `narration` from <project>/video.yaml, voices it with
en-GB-SoniaNeural, and writes per-scene:
    <project>/narration_edge/seg<i>.wav    24 kHz mono PCM (mega-shot import format)
    <project>/narration_edge/seg<i>.json   {voice, rate, words:[{word,start,end}]}
    <project>/narration_edge/index.yaml    seg -> scene id map (used by import step)

WordBoundary events are the whole point: they become `check.tu` in mega-shot,
which anchors subtitles and at_word cues to the real spoken words.

Usage:  python3 gen_narration.py <project_dir>
"""
import asyncio, json, os, sys
import yaml
import edge_tts

VOICE = os.environ.get("MYANG_VOICE", "en-GB-SoniaNeural")
RATE = os.environ.get("MYANG_TTS_RATE", "+0%")
PITCH = "+0Hz"


async def gen_one(text, out_wav, out_json):
    comm = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, boundary="WordBoundary")
    words, tmp = [], out_wav.replace(".wav", ".mp3")
    with open(tmp, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({"word": chunk["text"],
                              "start": round(chunk["offset"] / 1e7, 3),
                              "end": round((chunk["offset"] + chunk["duration"]) / 1e7, 3)})
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-v", "error", "-y", "-i", tmp, "-ar", "24000", "-ac", "1",
        "-c:a", "pcm_s16le", out_wav)
    await proc.wait()
    os.remove(tmp)
    json.dump({"voice": VOICE, "rate": RATE, "words": words}, open(out_json, "w"), indent=1)
    return words


async def main():
    if len(sys.argv) < 2:
        sys.exit("usage: gen_narration.py <project_dir>")
    proj = sys.argv[1]
    vdoc = yaml.safe_load(open(os.path.join(proj, "video.yaml")))
    outdir = os.path.join(proj, "narration_edge")
    os.makedirs(outdir, exist_ok=True)

    index, total = [], 0.0
    for i, scene in enumerate(vdoc["scenes"], 1):
        text = (scene.get("narration") or "").strip()
        if not text or text.startswith("#"):
            sys.exit(f"scene '{scene['id']}' has no narration — polish video.yaml first")
        wav, js = os.path.join(outdir, f"seg{i}.wav"), os.path.join(outdir, f"seg{i}.json")
        words = await gen_one(text, wav, js)
        dur = float(__import__("subprocess").run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav],
            capture_output=True, text=True).stdout.strip())
        total += dur
        index.append({"seg": i, "scene": scene["id"], "wav": wav, "json": js, "dur": dur})
        flag = "" if words else "  !! NO WORD BOUNDARIES"
        print(f"seg{i:<2} {scene['id']:<12} {dur:6.2f}s  {len(words):2d} words{flag}")
    yaml.safe_dump(index, open(os.path.join(outdir, "index.yaml"), "w"))
    print(f"TOTAL {total:.1f}s -> {outdir}")

asyncio.run(main())
