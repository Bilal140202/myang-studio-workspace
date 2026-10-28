#!/usr/bin/env python3
"""Publish pack generator — YouTube metadata + social captions from video.yaml.

Writes:
  <project>/out/youtube-publish-pack.md
  <project>/out/social-captions.md

Usage:  python3 publish_pack.py <project_dir> [--day N]
"""
import argparse, os, sys, datetime
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, "..", "topics.yaml")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proj")
    ap.add_argument("--day", type=int, default=None)
    a = ap.parse_args()
    proj = a.proj.rstrip("/")

    vdoc = yaml.safe_load(open(os.path.join(proj, "video.yaml")))
    pub = vdoc.get("publish") or {}
    titles = pub.get("titles") or []
    if not titles:
        sys.exit("video.yaml has no publish.titles")

    day_line = ""
    if a.day:
        bank = yaml.safe_load(open(BANK))
        meta = bank["meta"]
        d0 = datetime.date.fromisoformat(str(meta["start_date"]))
        pub_date = d0 + datetime.timedelta(days=a.day - 1)
        day_line = f"Publish date: **{pub_date.isoformat()}** (day {a.day})\n"

    slug = vdoc.get("name", os.path.basename(proj))
    os.makedirs(os.path.join(proj, "out"), exist_ok=True)

    yt = f"""# YouTube publish pack — {slug}

{day_line}
## Title (pick one, A/B later)
"""
    for i, t in enumerate(titles[:3], 1):
        yt += f"{i}. {t}\n"
    yt += f"""
## Description
{pub.get('hook', '')}

{pub.get('drama', '')}

{pub.get('trust', '')}

Filed under: beautiful — and lethal. New animal files daily.
#{' #'.join(t.replace(' ', '') for t in (pub.get('topics') or [])[:4])}

## Tags
{', '.join(pub.get('tags') or [])}

## Checklist
- [ ] Upload 9x16 (or 16x9 for long-form), original file, no re-encode
- [ ] Subtitle track: import out/*.srt (word-timed, verify first cue <= 1.5s)
- [ ] Thumbnail: out/anh_bia_khong-ngu.jpg (or custom)
- [ ] Pinned comment: "Which animal should get the next FILE? Myang is listening."
- [ ] End screen: none (Shorts) / next episode (long-form)
- [ ] Schedule: 06:00 local — morning commute + school-run peak
"""
    open(os.path.join(proj, "out", "youtube-publish-pack.md"), "w").write(yt)

    first_title = titles[0]
    tags = " ".join(f"#{t.replace(' ', '').lower()}" for t in (pub.get("topics") or [])[:5])
    soc = f"""# Social captions — {slug}

## TikTok / YT Shorts
{first_title} — but the real reason is better. {pub.get('drama', '')}
{tags} #myangstudi0

## Instagram Reels
Filed this one under "should not be possible". {pub.get('hook', '')}
{tags}

## X / Threads
{pub.get('hook', '')} Sources in the video — every single line. {tags}
"""
    open(os.path.join(proj, "out", "social-captions.md"), "w").write(soc)

    print(f"OK {os.path.join(proj, 'out', 'youtube-publish-pack.md')}")
    print(f"OK {os.path.join(proj, 'out', 'social-captions.md')}")


if __name__ == "__main__":
    main()
