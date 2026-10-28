# Myang Studio — Anti-AI-Slop YouTube Automation System

A production system that turns a researched topic bank into finished, word-timed, hand-drawn-style YouTube Shorts / Reels — with a strict anti-AI-slop QA gate at every stage and a studio mascot (**Myang**, the fluffy archive clerk) as the brand face.

**Final videos and all deliverable files are published via [GitHub Releases](../../releases) — see [DELIVERY.md](DELIVERY.md).**

## What's inside

| Path | What it is |
|------|-----------|
| `mega-shot/` | The video engine (vendored from [stevenguyenbt/mega-shot](https://github.com/stevenguyenbt/mega-shot), MIT). Whiteboard/puppet/hyperframes rendering, `xp` CLI: `new → narrate → art → mix → render → export → thumbnail`. |
| `download/content-engine/` | The 30-day content engine: `topics.yaml` (single source of truth — 30 days, 4 pillars, sourced facts, Myang beats), 30-day calendar (xlsx), playbook (docx), and `bin/` pipeline scripts. |
| `studio/videos/` | Per-video projects. `dolphins/` = shipped pilot (79s, en-GB-SoniaNeural, word-timed). `tardigrade-space/` = day-2 scaffold with word-timed draft narration. |
| `download/myang/` | Myang mascot kit: brand sheet, puppet sheet, 7 expressions (PNG + SVG). |
| `download/dolphins-video/` | Pilot deliverables (mp4, srt, thumbnail, publish pack, social captions). |
| `scripts/` | Tooling: `gen_edge_narration.py` (edge-tts + WordBoundary word timestamps), `patch_word_timings.py` (injects word times into mega-shot audio meta), Myang SVG generator, docx footer patcher. |
| `worklog.md` | Full build log of how the system was assembled. |

## Pipeline

```
topics.yaml (researched facts + citations)
   │
   ▼
new_video.py ──► video.yaml scaffold + nghien_cuu.md research desk
   │
   ▼
qa_gate.py (G1: banned-phrase regex · G2: evidence source check)
   │
   ▼
gen_edge_narration.py ──► per-scene WAV + word-level timing sidecars (edge-tts, WordBoundary)
   │
   ▼
patch_word_timings.py ──► word times injected into mega-shot audio meta
   │
   ▼
xp art ─► xp mix (-14 LUFS) ─► xp render ─► xp export
   │
   ▼
qa_gate.py (G3: timing coverage ≥90% · G4: LUFS -14±1 · G5: duration · G6: Myang budget ≤4 shots/≤3s · G7: pack presence)
   │
   ▼
publish_pack.py ─► GitHub Release  ◄── DELIVERY.md policy
```

## Anti-slop principles (enforced, not aspirational)

- Every fact carries a real citation (Nature, Science, WDC, Lyamin et al. — no "studies show").
- No banned buzzwords; the QA gate regexes them out at script stage.
- Subtitles are word-locked to the actual voice track (WordBoundary timestamps), never evenly spread.
- The mascot has a strict appearance budget — garnish, not filler.
- Loudness, duration and pack completeness are machine-checked before anything ships.

## Quickstart

```bash
# engine deps (first time)
cd mega-shot && bash bin/bootstrap.sh && cd ..

# scaffold day-2 video
python3 download/content-engine/bin/new_video.py tardigrade-space

# narration with word timestamps
python3 scripts/gen_edge_narration.py studio/videos/tardigrade-space

# render chain (from studio/ project root)
bash ../mega-shot/xp art && bash ../mega-shot/xp mix && MS_ENCODER=x264 bash ../mega-shot/xp render && bash ../mega-shot/xp export
```

## Credits

- [mega-shot](https://github.com/stevenguyenbt/mega-shot) by stevenguyenbt (MIT) — the rendering engine.
- huashu drawn styles and opuscar evidence-desk references included under their own licenses in `mega-shot/references/`.
- Narration: Microsoft Edge TTS neural voices.
