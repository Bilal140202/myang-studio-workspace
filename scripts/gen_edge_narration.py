#!/usr/bin/env python3
"""Generate narration with edge-tts (en-GB-SoniaNeural) + word-boundary timestamps.
Outputs per-scene WAV (24 kHz) + sidecar JSON with word timings (seconds, relative to audio start).
Usage: python gen_edge_narration.py <outdir>
"""
import asyncio, json, os, sys
import edge_tts

VOICE = "en-GB-SoniaNeural"   # soft, British, deadpan — the Sonia casting from the Myang plan
RATE = "+0%"
PITCH = "+0Hz"

TEXTS = [
    "Here's a puzzle. Dolphins are mammals, so they need air to breathe. But they live in the ocean. So how do they sleep without drowning?",
    "Humans breathe automatically. You never have to think about it. A dolphin's breath is voluntary. Every single breath is a conscious decision. Fall completely asleep, and a dolphin would stop breathing.",
    "So dolphins evolved a clever workaround. They sleep with only half of their brain at a time. The other half stays awake. Scientists call it unihemispheric slow-wave sleep.",
    "The sleeping half rests, while the awake half stays on duty. And here is the giveaway. A sleeping dolphin keeps one eye open. The eye on the opposite side of the sleeping half, watching for predators.",
    "They drift near the surface, resting motionless or swimming slowly, and rise every few minutes for a calm, easy breath. Over a full day, each half of the brain gets about four hours of sleep.",
    "New mothers do not get that luxury. For a whole month after a calf is born, mother and baby barely sleep at all.",
    "Half a brain asleep. One eye open. And still breathing. That is how a dolphin sleeps without drowning.",
]

async def gen_one(text: str, out_wav: str, out_json: str):
    comm = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, boundary="WordBoundary")
    words = []
    tmp_mp3 = out_wav.replace(".wav", ".mp3")
    with open(tmp_mp3, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({
                    "word": chunk["text"],
                    "start": round(chunk["offset"] / 1e7, 3),
                    "end": round((chunk["offset"] + chunk["duration"]) / 1e7, 3),
                })
    # mp3 → wav (pcm_s16le, 24 kHz mono) so mega-shot's import path accepts it
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-v", "error", "-y", "-i", tmp_mp3, "-ar", "24000", "-ac", "1",
        "-c:a", "pcm_s16le", out_wav)
    await proc.wait()
    os.remove(tmp_mp3)
    json.dump({"voice": VOICE, "rate": RATE, "words": words}, open(out_json, "w"), indent=1)
    return words

async def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "narration_edge"
    os.makedirs(outdir, exist_ok=True)
    total = 0.0
    for i, text in enumerate(TEXTS):
        wav = os.path.join(outdir, f"seg{i+1}.wav")
        js = os.path.join(outdir, f"seg{i+1}.json")
        words = await gen_one(text, wav, js)
        d = float(__import__("subprocess").run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav],
            capture_output=True, text=True).stdout.strip())
        total += d
        print(f"seg{i+1}: {d:6.2f}s  {len(words):2d} words  |  first: {words[0]['word'] if words else '-'} @ {words[0]['start'] if words else '-'}")
    print(f"TOTAL: {total:.1f}s")

asyncio.run(main())
