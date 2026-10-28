# Worklog

---
Task ID: 2
Agent: main agent (Z.ai)
Task: v2 — fix caption/voice sync, switch narration to Edge TTS (Sonia), adopt patterns from opuscar-studio; research youtube-automation-agent for the 30-day automation design

Work Log:
- User feedback: video good, but captions/VO misaligned; want edge-tts; check youtube-automation-agent + opuscar-studio; 30-day content automation with Myang mascot
- Researched youtube-automation-agent (6-stage loop: research→script→production→review→publish→learn, evidence desk, approval gates, shorts repurposing) and opuscar-studio (edge-tts permanent default, WordBoundary events per block → word-timed SRT + SFX alignment)
- Installed edge-tts 7.3.1; wrote scripts/gen_edge_narration.py: en-GB-SoniaNeural (per mascot-plan casting), boundary="WordBoundary" (default is SentenceBoundary — gotcha), per-scene wav + words sidecar JSON; 75.4s total
- Root cause of misalignment: mega-shot estimated word timings without VoiceStudio listen-back. Fix: patch build/audio/<id>.wav.json check.tu with Edge WordBoundary times (scripts/patch_word_timings.py), then xp timeline rebuilds word-anchored subtitles
- Learned: huashu at_word cues match DISPLAYED subtitle words (not narration). "rise"≠prefix of "rising"; digits displayed as "4" must be quoted in yaml; rewrote all cues to displayed words (hook draw at "dolphins", resting title at "4", etc.)
- Sandbox quirks: xp narrate import stalls mid-loop (VoiceStudio ping) → bypassed with direct cp + patch script; long processes SIGKILLed after producing valid artifacts; art/mix/render all recovered via caches
- Rebuilt: timeline 79.4s → art (0 warnings, cues word-locked) → mix -14 LUFS → render 2382 frames → export 79.3s 1080x1920
- Verified frames t=33/47/59: subtitles and pen-cues lock to spoken words; final file loudness -14.0 LUFS; SRT word-timed
- Updated /home/z/my-project/download/dolphins-video/ (video 7.8MB, srt, thumbnail, packs)

Stage Summary:
- Narration stack is now: edge-tts (en-GB-SoniaNeural) + WordBoundary JSON sidecars → meta patch → mega-shot timeline. Word-accurate subtitles + at_word visual cues, no VoiceStudio needed
- Reusable scripts: scripts/gen_edge_narration.py, scripts/patch_word_timings.py
- Key gotchas recorded: boundary param default, displayed-word matching for at_word, yaml numeric strings need quotes, import loop stalls → direct copy path
- Deliverables refreshed: download/dolphins-video/ (79s Sonia v2)

---
Task ID: 1
Agent: main agent (Z.ai)
Task: Clone and evaluate github.com/stevenguyenbt/mega-shot, then produce a finished video end-to-end in the sandbox

Work Log:
- Fetched repo README, AGENTS.md, SKILL.md; cloned to /home/z/my-project/mega-shot
- Determined feasibility: VoiceStudio (voice cloning) too heavy → decided to use z-ai TTS skill + `xp narrate --import-from`; stock APIs absent → used huashu drawn styles (no downloads); no GPU → MS_ENCODER=x264
- Ran `xp setup --install chromium huashu fonts` from project root /home/z/my-project/studio
- Created project: `xp new dolphins --format 9x16 --template footage`
- Researched dolphin sleep facts (WDC + Lyamin et al.) → videos/dolphins/nghien_cuu.md (8 sourced facts)
- Wrote videos/dolphins/video.yaml: 7 scenes, sketch/whiteboard (y3_whiteboard) cues, subtitles, publish block
- Generated 7 narration WAVs via z-ai TTS (voice jam), applied atempo=1.12 pitch-preserving tempo (96.8s → 85.5s)
- Imported narration: `xp narrate --import-from narration` → timeline 7 scenes · 89.5s · 21 subtitle lines
- Rendered whiteboard clips: `xp art` (7 mp4s + frame layers, cached)
- Mixed audio: `xp mix` → build/mix.wav, -14 LUFS, 7 auto SFX
- Rendered video: `xp render` with MS_ENCODER=x264 → 2683 frames, 131s, build/raw.mp4
- Exported: `xp export` → out/dolphins_9x16.mp4 (1080x1920, h264+aac, 89.3s), subtitles, publish pack
- `xp check` kept getting killed by sandbox watchdog → verified manually: frame extractions at 6/30/62/87s (visuals + subtitle sync OK), EBU R128 loudness of final file = -14.4 LUFS (target -14)
- Thumbnail: generated dolphin image (z-ai image skill), configured anh_bia.yaml, `xp thumbnail` → out/anh_bia_khong-ngu.jpg
- Copied deliverables to /home/z/my-project/download/dolphins-video/

Stage Summary:
- Full mega-shot pipeline proven end-to-end in sandbox WITHOUT VoiceStudio/API keys/GPU:
  TTS-import workaround for narration, huashu whiteboard for visuals, CPU x264 for encode
- Key scripts: /home/z/my-project/scripts/gen_narration.sh
- Video project: /home/z/my-project/studio/videos/dolphins (video.yaml, build/, out/)
- Deliverables: /home/z/my-project/download/dolphins-video/ (mp4 89s, srt, thumbnail, publish pack, social captions)
- Sandbox quirks: long-running xp processes sometimes SIGKILLed (-9) after producing valid output artifacts; re-runs hit per-scene caches, so recovery is cheap

---
Task ID: 3
Agent: main agent (Z.ai)
Task: Build the 30-day content automation engine (topic bank, scripts, calendar xlsx, playbook docx) with anti-slop gates + Myang integration spec

Work Log:
- Discovered sandbox reset had wiped mega-shot tooling; re-cloned repo (depth 1) — xp CLI needs `bash bin/bootstrap.sh` (step 4: npm deps) before first render
- Wrote topics.yaml — single source of truth: 30 days (pilot day 1 = dolphins), 4 pillars, hooks + 3 sourced facts/day (real citations: Patek 2004 Nature, Barnes 1989 Science, Nielsen 2016 Science, etc.), Myang beat per day, 4 weekly long-forms with reuse lists
- Built engine at download/content-engine/: topics.yaml, 30-day-content-calendar.xlsx, content-engine-playbook.docx, README.md, bin/{bootstrap.sh,new_video.py,gen_narration.py,import_narration.py,render.sh,qa_gate.py,publish_pack.py,make_calendar.py}
- Calendar xlsx: 4 sheets (Calendar/Topic Bank/Long-forms/Production) via xlsx skill base.py; QA chain recalc/audit/scan/validate all clean, exit 0
- Playbook docx: R1 cover + GO-1 palette, TOC (Roman) + body (Arabic), 8 tables, 2 Myang figures, ~3.5k words; add_toc_placeholders exit 0; postcheck 0 errors (1 benign table-cell line-spacing warning); footers patched \* ROMAN / \* arabic, empty pgNumType removed
- Fixed scaffolder bugs: unquoted YAML colons -> JSON-quoted scalars; em-dash mangling -> safe sentence split
- QA gate (G1-G7): banned-phrase regex, evidence-source check, WordBoundary timing coverage >=90%, LUFS -14±1, duration windows, Myang budget (<=4 reactions, <=3s), pack presence; pre-render mode downgrades render-stage gates to warnings
- Smoke-tested full chain on day-2 (tardigrade-space): scaffold OK -> script gate PASS -> narration 5 segs / 37.1s with word timestamps

Stage Summary:
- Engine operational: new_video.py -> polish -> qa_gate (script) -> gen_narration.py -> import_narration.py -> render.sh -> qa_gate (full) -> publish_pack.py
- Day-2 project scaffolded at studio/videos/tardigrade-space with research desk + word-timed draft narration; next human step: polish narration + add at_word cues, run bootstrap for xp deps, render
- Anti-slop enforced by gate G1-G7; Myang spec (4 appearances, budget) documented in playbook §7 and enforced by G6
