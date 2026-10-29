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

---
Task ID: 4
Agent: main agent (Z.ai)
Task: Publish system to GitHub; delivery switched to Git Releases (standing policy)

Work Log:
- Published ansaribilal14/myang-studio (752 files) + release v1.0.0 (8 assets) — superseded by Task 5 account move
- DELIVERY.md: releases are the ONLY delivery channel; tag vMAJOR.MINOR.PATCH[+dayN]; video asset checklist

---
Task ID: 5
Agent: main agent (Z.ai)
Task: Sandbox-wipe recovery, backup repo, caption-free v1.1 rebuild + ASR-verified SRT + release

Work Log:
- Confirmed user's warning: sandbox wiped publish.git, scripts/make_release.py, mascot zip, README/DELIVERY (worklog survived but stale)
- Recovered wiped files by cloning ansaribilal14/myang-studio (new token has pull there)
- New token belongs to account Bilal140202 (push access to ansaribilal14 = pull only) -> canonical repos moved:
  * Bilal140202/myang-studio = system + releases
  * Bilal140202/myang-studio-workspace = full working-state backup (3581 files; build artifacts incl., render frame layers excluded) — pushed after every work chunk
- Two gitdirs over one worktree: publish.git (lean; strict excludes in publish.git/info/exclude) + backup.git (superset)
- Caption desync root cause: paraphrased display text aligned by cumulative syllable ratio -> captions raced ahead of narration
- Fix per user directive: NO burned captions; captions = separate SRT. video.yaml subtitles -> verbatim; at_word cues -> narration words (rising->rise, "4"->four); xp timeline -> 48 word-locked cues (ocean 5.662 vs meta 5.675)
- xp art rebuilt 7 scenes (chromium+huashu reinstalled post-wipe); subs stripped from timeline.json pre-render (cue specs cached) -> caption-free render 2382 frames, export 79.3s -14.0 LUFS
- Frame-verified t=2..77: whiteboard draws word-anchored, zero burned captions
- ASR (z-ai): 30s/file limit -> split mix at scene boundaries, 16kHz mono; merged 197 words = 100% SRT vocabulary match
- Release v1.1.0 (Bilal140202/myang-studio): mp4 5.9MB + srt + thumbnail + publish pack + social captions

Stage Summary:
- Caption sync proof: ASR-on-final-audio == SRT text (100%)
- Recover-after-wipe = clone Bilal140202/myang-studio-workspace
- Pending: mascot redesign (user rejected v1), RPG game (requested next), day-2 tardigrade render
---
Task ID: 6
Agent: main agent (Z.ai)
Task: Day-2 tardigrade-space — polish, render, caption-free export, ASR proof, pack (v1.1 pipeline)

Work Log:
- Sandbox reset #3 detected (publish.git/backup.git/gh credentials/gh CLI gone; mega-shot vendor wiped). Rebootstrapped: edge-tts 7.3.1, xp setup --install chromium,huashu,fonts (--quick --no-launch). xp binary lives at mega-shot/xp (NOT mega-shot/bin/xp)
- Draft narration was 37.1s / 5 scenes -> would fail G5 (45-120s). Expanded to 7 scenes / 93.4s narration with elaboration only: 3 sourced facts unchanged (Jonsson 2008 x2, Tsujimoto 2016), no new stats (water-bear nickname, 8 legs, tun=barrel are anatomy/common knowledge, same freedom as pilot)
- v1.1 caption policy applied: subtitles verbatim narration, at_word cues anchor NARRATION words. New scripts/check_cue_anchors.py verifies every at_word is an exact WordBoundary token + highlight targets resolve: 21/21 PASS
- New scripts/prep_caption_free.py: caches timeline subs -> build/subs_backup.json/.srt, emits word-timed <name>.en.srt, strips subs from timeline.json (caption-free render)
- GOTCHA: xp render needs film.html in the project dir (new_video.py scaffold omits it) -> copied generic footage-template film.html from dolphins (handles loai:huashu scenes via build/layers). xp render 2922 frames/135s OK; art+mix cached after one 600s timeout
- GOTCHA: xp export SIGKILLed by watchdog AFTER writing all out/ artifacts (known pattern) - artifacts valid
- Verify: 1080x1920 h264+aac 97.3s, ebur128 -14.0 LUFS, frames t=2.5/8/15/30/44/58/75/92 word-locked, zero burned captions, out/subtitles empty
- New scripts/asr_verify.sh: split FINAL mix at scene boundaries (<=25s chunks, 16kHz mono) -> z-ai asr -> vocab match vs SRT = 98.5% (202/205; deltas: '2007'<->'two thousand seven', tardigrades<->tardigrade, tun<->ton homophone) = sync proof
- Thumbnail: 4 generations (2 too seal/sloth-like, 1 too zoomed portrait) -> landscape 1344x768 source with subject right + empty-left, anh_bia.yaml (mau_nhan #ff6a2b), xp thumbnail -> out/anh_bia_khong-ngu.jpg. Lesson: thumbnail source must be LANDSCAPE with subject on right third or the crop eats the subject
- publish_pack.py --day 2; drama line de-duplicated from hook; topics.yaml day-2 status -> shipped; qa_gate full PASS
- GitHub release NOT cut: no gh CLI, no token in env (died with sandbox). Deliverables staged in download/tardigrade-video/ awaiting token to push Bilal140202/myang-studio release v1.1.0+day2

Stage Summary:
- Day 2 shipped locally: download/tardigrade-video/ (mp4 97.3s, word-timed srt 49 cues, thumbnail, publish pack, social captions)
- New reusable scripts: check_cue_anchors.py, prep_caption_free.py, asr_verify.sh
- Pipeline gotchas recorded: film.html required by xp render; thumbnail source orientation; xp export SIGKILL-after-write
- Blocked on user: fresh GitHub token (push + release) for v1.1.0+day2

---
Task ID: 7
Agent: main agent (Z.ai)
Task: Unblock with fresh GitHub token (Bilal140202) — cut blocked v1.1.0+day2 release, finish teaser, backup day-3 sources

Work Log:
- Context restored from worklog after session compaction; user provided new token (scopes: repo, workflow, write:packages) + reference repo links
- Remote check: v1.2.0 (Ember Crypt RPG) had been cut in the lost session tail; v1.1.0+day2 (tardigrade) still missing = the known blocked item
- Disk full (100%): cleared browser caches (1.9G) + released projects' build dirs (dolphins/tardigrade 479M, finals safe in download/ + Releases)
- RELEASED v1.1.0+day2 — Tardigrade in space (id 427568198): mp4 97.3s 1080x1920 -14.0 LUFS + word-timed SRT 49 cues + thumbnail + publish pack + social captions (5 assets)
- Day-3 procrastination-fix series found mid-production: teaser rendered-raw, tap-01..03 mixed, tap-04..06 narration only; kichban_master.py = 6 episodes + teaser, gate-tuned verbatim scripts (Steel 2007, Sirois & Pychyl 2013)
- Workspace backup had ZERO procrastination entries -> pushed 36M of sources (7 projects: narration wav+WordBoundary json, video.yaml, film.html, research, CC licenses, imgpool manifests) via partial clone (blob:none + sparse-checkout + `git add --sparse` gotcha) -> 335513b
- Teaser export completed via known SIGKILL-after-write pattern: 1920x1080 32.6s h264+aac; frames t=5/20 caption-free (labels only); ebur128 -14.1 LUFS
- Built teaser.en.srt from timeline_subs_backup.json (19 cues, 0.19..30.82s); subs_backup.json must be a BARE LIST for asr_verify.sh (dict wrapper broke the merge step)
- ASR sync proof: 97.8% vocab match (91/93; '5'<->five, isn't tokenization; chunks.json glob noise explained)
- RELEASED v1.3.0+day3-teaser — The Loop (id 427577845): mp4 56M + SRT + thumbnail (t=5.2 title card) + publish pack + social captions + image-credits.md (6 assets)
- Staged deliverables: download/tardigrade-video/ (already), download/teaser-video/ (new)

Stage Summary:
- All blocked releases cleared: v1.1.0+day2 + v1.3.0+day3-teaser now live on Bilal140202/myang-studio
- Day-3 series state: teaser SHIPPED; tap-01..03 next (assets->mix->strip->render->export->srt->release), tap-04..06 need narration import + mix first
- Scripts added: build_proc_srt.py (generic proc-series SRT from subs backup), stage_teaser.sh, cut_release_day2.sh, cut_release_teaser.sh
- Token stored in session scripts only (never committed); releases-only delivery policy upheld
