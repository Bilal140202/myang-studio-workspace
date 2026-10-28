# Delivery Policy — Git Releases Only

**Effective immediately, all files and final videos are delivered through GitHub Releases on this repository. Nothing is shipped through chat file listings anymore.**

## Rules

1. **Releases are the only delivery channel.** Every finished video, document, dataset, or asset pack must be attached to a GitHub Release. The repo holds sources; Releases hold artifacts.
2. **One release per publishable unit.** A finished short, a long-form episode, an engine upgrade, or a new mascot asset pack each get their own release.
3. **Tag naming:** `vMAJOR.MINOR.PATCH` for the system (engine, docs, mascot kit) and `vMAJOR.MINOR.PATCH+dayN` for a content day (e.g. `v1.0.0+day1` = the dolphins pilot).
4. **Mandatory asset checklist for every video release:**
   - `*.mp4` — final export (1080x1920 or 1920x1080, -14 LUFS)
   - `*.srt` — word-timed subtitles
   - `thumbnail.jpg`
   - `youtube-publish-pack.md` (title, description, tags, chapters)
   - `social-captions.md` (IG/TikTok/Shorts copy)
5. **Never commit secrets.** Tokens, `.env`, API keys stay out of the repo — see mega-shot's `tools/secret_scan.py`.
6. **Release notes must include:** duration, resolution, loudness, narration voice, QA gate results, and the topic-bank day number.

## Cutting a release (commands)

```bash
# 1. Commit and push the sources that produced the artifacts
git add -A && git commit -m "day N: <topic>"
git push origin main

# 2. Create the release
gh release create "v1.0.0+dayN" \
  out/<video>.mp4 out/<video>.en.srt thumbnail.jpg \
  youtube-publish-pack.md social-captions.md \
  --title "Day N — <topic>" \
  --notes "QA: G1-G7 PASS · -14 LUFS · 1080x1920 · voice: en-GB-SoniaNeural"
```

(Without the `gh` CLI, create the release via the GitHub API: `POST /repos/ansaribilal14/myang-studio/releases`, then upload assets to `uploads.github.com`.)
