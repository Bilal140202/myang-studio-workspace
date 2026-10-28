#!/usr/bin/env python3
"""Scaffold a new video project from the topic bank (topics.yaml).

Creates  <STUDIO>/videos/<slug>/video.yaml  with:
  - publish block (titles/hook/topics/tags from the topic row)
  - scenes: hook + one scene per sourced fact + outro  (narration pre-filled
    from the checked fact sentences; polish freely, keep the facts)
The yaml follows the proven mega-shot schema used by the dolphins pilot.

Usage:  python3 new_video.py <slug> [--format 9x16|16x9] [--day N]
"""
import argparse, json, os, sys
import yaml


def yq(text):
    """Yaml-safe double-quoted scalar (JSON strings are valid YAML scalars)."""
    return json.dumps(str(text), ensure_ascii=False)

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, "..", "topics.yaml")
STUDIO = os.environ.get("MYANG_STUDIO", "/home/z/my-project/studio")


def load_bank():
    with open(BANK) as f:
        return yaml.safe_load(f)


def fmt_seconds_line(text):
    return text.strip()


def scaffold(day_row, meta, fmt):
    slug = day_row["slug"]
    is_long = day_row["format"] == "long"
    sid_words = ["first", "second", "third", "fourth", "fifth"]

    scenes = []
    # 1) hook scene — narration is the approved hook line itself
    scenes.append({
        "id": "hook",
        "narration": day_row["hook"],
        "subtitle": f"**{day_row['title']}.**",
    })
    # 2) one scene per sourced fact (long-form rows get a note instead)
    for i, fw in enumerate(day_row.get("facts", [])):
        if "Long-form compilation" in fw["fact"]:
            scenes.append({
                "id": f"f{i+1}",
                "narration": f"POLISH ME - write connective narration reusing the "
                             f"scene banks of reuses: {day_row.get('reuses', [])}",
                "subtitle": f"Chapter {i+1}. | POLISH ME",
            })
            continue
        fact = fw["fact"].replace(" — ", " -- ")          # keep em-dash grouping intact
        sentences = [s.strip() for s in fact.split(". ") if s.strip()]
        lead = ". ".join(sentences[:2])
        if len(sentences) > 1 and not lead.endswith("."):
            lead += "."
        lines = [s.rstrip(".") for s in sentences[:3]]
        scenes.append({
            "id": f"f{i+1}",
            "narration": lead,
            "subtitle": " | ".join(f"**{s}**." for s in lines),
        })
    # 3) outro — archivist stamp cadence
    scenes.append({
        "id": "outro",
        "narration": f"That is how {day_row['title'].lower().replace('the ', '')} — filed, checked, and stamped.",
        "subtitle": "**Filed.** | Checked against the research. | **Stamped.**",
    })

    yaml_lines = [
        f"# {day_row['title']} — {fmt} sketch/whiteboard (EN)",
        "# Voice: Edge TTS en-GB-SoniaNeural. Cues use at_word on DISPLAYED subtitle words.",
        "# Anti-slop: polish narration freely, but facts/sources may not change.",
        f"name: {slug}",
        f"format: {fmt}",
        "language: en",
        "voice: { sample: documentarian, volume: 0.55, speed: 1.0 }",
        "sfx: { level: 1.0, ambience: khong }",
        "style: { subtitle_style: box }",
        "publish:",
        "  titles:",
        f"    - {yq(day_row['title'])}",
        f"    - {yq(day_row['hook'])}",
        f"    - {yq(day_row['title'] + ' — the animal file nobody expects')}",
        f"  hook: {yq(day_row['hook'])}",
        "  topics: [" + ", ".join(yq(t) for t in [
            "animal facts", "weird biology", "nature shorts", day_row["pillar"]]) + "]",
        f"  drama: {yq(day_row['hook'])}",
        f"  trust: {yq('Every fact sourced in nghien_cuu.md. Day %d of the 30-day bank.' % day_row['day'])}",
        "  tags: [" + ", ".join(yq(t) for t in [
            slug.replace("-", ""), "animalfacts", day_row["pillar"], "learnontiktok", "myang"]) + "]",
        "",
        "scenes:",
    ]
    for sc in scenes:
        yaml_lines.append(f"  - id: {sc['id']}")
        yaml_lines.append(f"    narration: {yq(sc['narration'])}")
        yaml_lines.append(f"    subtitle: {yq(sc['subtitle'])}")
        yaml_lines.append("    huashu:")
        yaml_lines.append(f"      grammar: {meta['visual_grammar']}")
        yaml_lines.append("      cues: []   # add at_word cues AFTER polish (word must be DISPLAYED)")
        yaml_lines.append("")
    return "\n".join(yaml_lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--format", default=None, choices=["9x16", "16x9"])
    ap.add_argument("--day", type=int, default=None, help="verify the slug matches this day")
    a = ap.parse_args()

    bank = load_bank()
    rows = [d for d in bank["days"] if d["slug"] == a.slug]
    if not rows:
        sys.exit(f"slug '{a.slug}' not in topics.yaml — available: "
                 + ", ".join(d["slug"] for d in bank["days"]))
    row = rows[0]
    if a.day and row["day"] != a.day:
        sys.exit(f"slug '{a.slug}' is day {row['day']}, not day {a.day}")
    fmt = a.format or ("16x9" if row["format"] == "long" else "9x16")

    proj = os.path.join(STUDIO, "videos", a.slug)
    os.makedirs(proj, exist_ok=True)
    out = os.path.join(proj, "video.yaml")
    if os.path.exists(out):
        sys.exit(f"refusing to overwrite {out}")

    with open(out, "w") as f:
        f.write(scaffold(row, bank["meta"], fmt))

    # copy the sourced facts into the project research desk
    with open(os.path.join(proj, "nghien_cuu.md"), "w") as f:
        f.write(f"# Research — {row['title']} (day {row['day']})\n\n")
        for i, fw in enumerate(row.get("facts", []), 1):
            f.write(f"{i}. {fw['fact']}\n   Source: {fw['source']}\n\n")
        f.write(f"Hook: {row['hook']}\nMyang beat: {row['myang']}\n")

    print(f"OK  {out}")
    print(f"OK  {os.path.join(proj, 'nghien_cuu.md')}")
    print("next: polish video.yaml -> bin/qa_gate.py script-gate -> bin/gen_narration.py")


if __name__ == "__main__":
    main()
