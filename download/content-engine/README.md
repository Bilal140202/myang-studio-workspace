# Myang Studio Content Engine

A 30-day, anti-AI-slop content pipeline for the **Myang Studio** faceless channel,
built on the proven mega-shot stack (`xp` CLI) + Edge-TTS word-timed narration.

- Niche: **animal survival engineering — how animals do impossible things**
- Voice (locked): `en-GB-SoniaNeural` — soft British deadpan, matches Myang
- Visuals: huashu `y3_whiteboard` drawn-in-code clips (no stock footage, no downloads)
- Loudness: **-14 LUFS** (YouTube standard), verified per video
- Subtitles: **word-timed** from Edge-TTS WordBoundary events (never uniform fallback)

## Layout

```
content-engine/
├── topics.yaml                  ← SINGLE SOURCE OF TRUTH (30 days: hooks, facts, sources, Myang beats)
├── 30-day-content-calendar.xlsx ← generated view of topics.yaml (Calendar / Topic Bank / Long-forms / Production)
├── content-engine-playbook.docx ← full system documentation
└── bin/
    ├── bootstrap.sh             ← restore toolchain after a machine reset (clone xp, install edge-tts)
    ├── new_video.py             ← scaffold studio/videos/<slug>/ from a topic row (+ research desk)
    ├── gen_narration.py         ← Edge-TTS narration + WordBoundary JSON sidecars
    ├── import_narration.py      ← copy wavs into build/audio, patch check.tu word timings, xp timeline
    ├── render.sh                ← xp art → mix → render → export (MS_ENCODER=x264 on CPU)
    ├── qa_gate.py               ← anti-slop gates G1–G7 (must PASS before publish)
    ├── publish_pack.py          ← YouTube metadata pack + social captions
    └── make_calendar.py         ← regenerate the xlsx calendar from topics.yaml
```

## Daily run (one short)

```bash
cd /home/z/my-project/download/content-engine

# 0. once, or after any sandbox/machine reset
bash bin/bootstrap.sh

# 1. scaffold today's video from the topic bank (e.g. day 2 → tardigrade-space)
python3 bin/new_video.py tardigrade-space

# 2. HUMAN PASS: polish narration + subtitles in studio/videos/<slug>/video.yaml
#    - keep facts exactly as sourced
#    - add at_word cues AFTER polish (anchor word must be a DISPLAYED subtitle word;
#      "rise" ≠ "rising"; digits displayed as "4" must be quoted in yaml)
# 3. script gate before spending render time
python3 bin/qa_gate.py ../studio/videos/<slug> --short        # G1+G2 pass

# 4. narration with real word timestamps
python3 bin/gen_narration.py ../studio/videos/<slug>
python3 bin/import_narration.py ../studio/videos/<slug>

# 5. render (safe to re-run: per-scene caches; SIGKILLed jobs resume cheap)
bash bin/render.sh ../studio/videos/<slug>

# 6. full gate + publish pack
python3 bin/qa_gate.py ../studio/videos/<slug> --short
python3 bin/publish_pack.py ../studio/videos/<slug> --day 2
```

## Long-form Sundays (days 7 / 14 / 21 / 28)

The compilation replaces the daily short. `new_video.py <longform-slug>` scaffolds a
chaptered project; pull the researched scene banks from the reused days listed in
`topics.yaml → longform.reuses`, add connective narration, and render `16x9`.
Myang appears on chapter cards (evidence pose) and the end stamp only.
Instagram gets 2–3 reel cutdowns carved from the long-form.

## The anti-slop gates (qa_gate.py)

| Gate | Check | Fail condition |
|------|-------|----------------|
| G1 | Banned AI-slop phrases ("dive into", "unleash", "mind-blowing", …) | any hit in narration/subtitles/titles |
| G2 | Evidence desk | any fact without a `Source:` line |
| G3 | Word timings | empty `check.tu` (uniform fallback), coverage < 90% |
| G4 | Loudness | outside [-15.0, -13.0] LUFS |
| G5 | Duration | short outside 45–120 s; long outside 7–14 min |
| G6 | Myang budget | > 4 corner reactions, or any reaction > 3 s |
| G7 | Publish pack | missing |

**Exit 0 = safe to publish. Nothing ships around the gate.**

## Sandbox survival notes (learned from the dolphins pilot)

- Long `xp` jobs can be SIGKILLed **after** writing valid artifacts — re-run; per-scene
  caches make recovery cheap. `render.sh` retries each stage once.
- `xp narrate --import-from` stalls on a VoiceStudio ping in this environment —
  `import_narration.py` bypasses it (direct copy + meta patch), same as the v2 pilot.
- `MS_ENCODER=x264` forces CPU encoding (no GPU in sandbox).
- Verify manually when `xp check` cannot finish: extract frames with ffmpeg and run
  `ffmpeg -i out/final.mp4 -af ebur128 -f null -` for loudness.

## Myang usage rules (enforced in spirit by G6)

1. Chapter cards (long-form only, evidence pose) 2. Glasses-on evidence inspection
3. Corner reactions: ≤ 4/video, ≤ 3 s each, never on serious beats 4. End stamp
("FILED" → *"Filed under: beautiful — and lethal"*). 90% of screen time: unimpressed.
