/* Myang Studio — 30-Day Content Engine Playbook (.docx)
 * Recipe: R1 (Pure Paragraph Left) + GO-1 Graphite Orange (long-title override from R4/proposal)
 * Profile A formal English (Times New Roman), 3-section numbering, TOC + refresh hint.
 */
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  PageBreak, Header, Footer, PageNumber, NumberFormat, AlignmentType, HeadingLevel,
  WidthType, BorderStyle, ShadingType, SectionType, TableLayoutType, TableOfContents,
} = require("docx");
const fs = require("fs");

/* ── palette: GO-1 Graphite Orange (proposals / PRD) ─────────────────────── */
const P = {
  bg: "1A2330", accent: "D4875A",
  titleColor: "FFFFFF", subtitleColor: "B0B8C0", metaColor: "90989F", footerColor: "687078",
  headText: "1A2330", body: "000000", gray: "808080",
  tHeaderBg: "D4875A", tHeaderText: "FFFFFF", tInner: "DDD0C8", tSurface: "F8F0EB",
};

const NB = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: NB, bottom: NB, left: NB, right: NB };
const allNoBorders = { ...noBorders, insideHorizontal: NB, insideVertical: NB };

/* ── cover layout engine (from design-system.md) ─────────────────────────── */
function splitTitleLines(title, cpl) {
  if (title.length <= cpl) return [title];
  const breakAfter = new Set([..."，。、；：！？", ..."的与和及之在于为", ..."-_—–·/", ..." \t"]);
  const lines = []; let rem = title;
  while (rem.length > cpl) {
    let at = -1;
    for (let i = cpl; i >= Math.floor(cpl * 0.6); i--)
      if (i < rem.length && breakAfter.has(rem[i - 1])) { at = i; break; }
    if (at === -1) {
      const lim = Math.min(rem.length, Math.ceil(cpl * 1.3));
      for (let i = cpl + 1; i < lim; i++)
        if (breakAfter.has(rem[i - 1])) { at = i; break; }
    }
    if (at === -1) at = cpl;
    lines.push(rem.slice(0, at).trim()); rem = rem.slice(at).trim();
  }
  if (rem) lines.push(rem);
  if (lines.length > 1 && lines[lines.length - 1].length <= 2)
    lines[lines.length - 2] += lines.pop();
  return lines;
}
function calcTitleLayout(title, maxW, prefPt = 40, minPt = 24) {
  const cw = (pt) => pt * 20;
  let pt = prefPt, lines;
  while (pt >= minPt) {
    const cpl = Math.floor(maxW / cw(pt));
    if (cpl < 2) { pt -= 2; continue; }
    lines = splitTitleLines(title, cpl);
    if (lines.length <= 3) break;
    pt -= 2;
  }
  if (!lines || lines.length > 3) { lines = splitTitleLines(title, Math.floor(maxW / cw(minPt))); pt = minPt; }
  return { titlePt: pt, titleLines: lines };
}
function calcCoverSpacing(p) {
  const { titleLineCount = 1, titlePt = 36, hasSubtitle = false, hasEnglishLabel = false,
    metaLineCount = 0, fixedHeight = 800, pageHeight = 16838, marginTop = 0, marginBottom = 0 } = p;
  const SAFETY = 1200;
  const usable = pageHeight - marginTop - marginBottom - SAFETY;
  const content = titleLineCount * (titlePt * 23 + 200) + (hasSubtitle ? (12 * 23 + 600) : 0) +
    (hasEnglishLabel ? (9 * 23 + 600) : 0) + metaLineCount * (10 * 23 + 100) + fixedHeight + 3 * 300;
  const rem = Math.max(usable - content, 400);
  const FOOTER_MIN = 800;
  const rawTop = Math.floor(rem * 0.45), rawBottom = Math.floor(rem * 0.45);
  const bottomSpacing = Math.max(rawBottom, FOOTER_MIN);
  const topSpacing = Math.max(rawTop - Math.max(0, FOOTER_MIN - rawBottom), 400);
  return { topSpacing, midSpacing: Math.max(rem - topSpacing - bottomSpacing, 0), bottomSpacing };
}
function buildCoverR1(cfg) {
  const padL = 1200, padR = 800;
  const { titlePt, titleLines } = calcTitleLayout(cfg.title, 11906 - padL - padR - 300, 40, 24);
  const sp = calcCoverSpacing({
    titleLineCount: titleLines.length, titlePt, hasSubtitle: !!cfg.subtitle,
    hasEnglishLabel: !!cfg.englishLabel, metaLineCount: (cfg.metaLines || []).length, fixedHeight: 400,
  });
  const accentLeft = { style: BorderStyle.SINGLE, size: 8, color: P.accent, space: 12 };
  const ch = [];
  ch.push(new Paragraph({ spacing: { before: sp.topSpacing } }));
  ch.push(new Paragraph({
    indent: { left: padL, right: padR }, spacing: { after: 500 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: P.accent, space: 8 } },
    children: [new TextRun({ text: cfg.englishLabel.split("").join("  "), size: 18, color: P.accent,
      font: { ascii: "Arial", eastAsia: "SimHei" }, characterSpacing: 40 })],
  }));
  titleLines.forEach((ln, i) => ch.push(new Paragraph({
    indent: { left: padL },
    spacing: { after: i < titleLines.length - 1 ? 100 : 300, line: Math.ceil(titlePt * 23), lineRule: "atLeast" },
    children: [new TextRun({ text: ln, size: titlePt * 2, bold: true, color: P.titleColor,
      font: { ascii: "Arial", eastAsia: "SimHei" } })],
  })));
  if (cfg.subtitle) ch.push(new Paragraph({
    indent: { left: padL }, spacing: { after: 800 },
    children: [new TextRun({ text: cfg.subtitle, size: 24, color: P.subtitleColor,
      font: { ascii: "Arial", eastAsia: "Microsoft YaHei" } })],
  }));
  for (const line of (cfg.metaLines || [])) ch.push(new Paragraph({
    indent: { left: padL + 200 }, spacing: { after: 80 }, border: { left: accentLeft },
    children: [new TextRun({ text: line, size: 24, color: P.metaColor,
      font: { ascii: "Arial", eastAsia: "Microsoft YaHei" } })],
  }));
  ch.push(new Paragraph({ spacing: { before: sp.bottomSpacing } }));
  ch.push(new Paragraph({
    indent: { left: padL, right: padR },
    border: { top: { style: BorderStyle.SINGLE, size: 2, color: P.accent, space: 8 } },
    spacing: { before: 200 },
    children: [
      new TextRun({ text: cfg.footerLeft || "", size: 16, color: P.footerColor, font: { ascii: "Arial" } }),
      new TextRun({ text: "                                        " }),
      new TextRun({ text: cfg.footerRight || "", size: 16, color: P.footerColor, font: { ascii: "Arial" } }),
    ],
  }));
  return [new Table({
    width: { size: 100, type: WidthType.PERCENTAGE }, layout: TableLayoutType.FIXED,
    borders: allNoBorders,
    rows: [new TableRow({
      height: { value: 16838, rule: "exact" },
      children: [new TableCell({
        shading: { type: ShadingType.CLEAR, fill: P.bg }, borders: noBorders, children: ch,
      })],
    })],
  })];
}

/* ── body helpers ────────────────────────────────────────────────────────── */
const F = { ascii: "Times New Roman", eastAsia: "SimSun" };
const FH = { ascii: "Times New Roman", eastAsia: "SimHei" };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 160, line: 312 },
    children: [new TextRun({ text, bold: true, size: 32, color: P.headText, font: FH })],
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120, line: 312 },
    children: [new TextRun({ text, bold: true, size: 28, color: P.headText, font: FH })],
  });
}
function body(text, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED, spacing: { line: 312, after: 120 },
    children: [new TextRun({ text, size: 24, color: P.body, font: F, ...opts })],
  });
}
function bodyRuns(runs) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED, spacing: { line: 312, after: 120 },
    children: runs.map(r => new TextRun({ size: 24, color: P.body, font: F, ...r })),
  });
}
function bullet(text) {
  return new Paragraph({
    bullet: { level: 0 }, spacing: { line: 312, after: 80 },
    children: [new TextRun({ text, size: 24, color: P.body, font: F })],
  });
}
function caption(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 80, after: 200 },
    children: [new TextRun({ text, size: 18, color: P.gray, italics: true, font: F })],
  });
}
function tblTitle(text) {
  return new Paragraph({
    keepNext: true, spacing: { before: 200, after: 100 },
    children: [new TextRun({ text, bold: true, size: 21, color: P.headText, font: F })],
  });
}
function cell(text, { header = false, w = 20, fill = null, align = AlignmentType.LEFT } = {}) {
  return new TableCell({
    width: { size: w, type: WidthType.PERCENTAGE },
    shading: fill ? { type: ShadingType.CLEAR, fill } : undefined,
    margins: { top: 60, bottom: 60, left: 120, right: 120 },
    children: [new Paragraph({
      alignment: align, spacing: { line: 276 },
      children: [new TextRun({
        text, size: 20, bold: header, font: F,
        color: header ? P.tHeaderText : P.body,
      })],
    })],
  });
}
function tbl(headers, rows, widths) {
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: P.accent },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: P.accent },
      left: NB, right: NB,
      insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: P.tInner },
      insideVertical: NB,
    },
    rows: [
      new TableRow({
        tableHeader: true, cantSplit: true,
        children: headers.map((t, i) => cell(t, { header: true, w: widths[i], fill: P.tHeaderBg })),
      }),
      ...rows.map((r, ri) => new TableRow({
        cantSplit: true,
        children: r.map((t, i) => cell(t, { w: widths[i], fill: ri % 2 === 1 ? P.tSurface : null })),
      })),
    ],
  });
}
function figure(path, w, h) {
  return new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 200, after: 40 },
    children: [new ImageRun({ data: fs.readFileSync(path), transformation: { width: w, height: h }, type: "png" })],
  });
}

/* ── footers ─────────────────────────────────────────────────────────────── */
function romanFooter() {
  return new Footer({ children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "807F80" })], // marker color → ROMAN
  })] });
}
function arabicFooter() {
  return new Footer({ children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "808080" })],
  })] });
}
function pageHeader() {
  return new Header({ children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Myang Studio — 30-Day Content Engine Playbook", size: 18, color: P.gray, font: F })],
  })] });
}

/* ══ BODY CONTENT ═════════════════════════════════════════════════════════ */
const bodyChildren = [];

/* 1 ─ Executive Summary */
bodyChildren.push(h1("1. Executive Summary"));
bodyChildren.push(body("This playbook documents the Myang Studio content engine: a 30-day production system that turns one research desk, one locked voice, and one drawn-visual style into a daily publishing cadence without sliding into AI slop. The engine was designed after a full end-to-end pilot — a 79-second short on dolphin sleep — proved every stage of the pipeline in real conditions, including word-accurate subtitles, loudness at -14 LUFS, and a complete publish pack. The pilot matters because nothing in this document is theoretical; each command listed here has already produced a finished, published artifact."));
bodyChildren.push(body("The engine produces one vertical short per day (55 to 95 seconds, whiteboard sketch style, narrated by the locked Edge-TTS voice Sonia) plus a weekly 16x9 long-form compilation every seventh day. Every piece of content passes through seven hard quality gates before release, covering banned phrasing, sourced evidence, word-level subtitle timing, loudness, duration, mascot usage budget, and packaging. The mascot — Myang, a cream-plush archivist with a brass stamp — appears under strict cameo rules so the channel builds a recognisable brand asset without becoming a gimmick."));
bodyChildren.push(body("The deliverables that accompany this playbook are the topic bank (topics.yaml, the single source of truth), the generated 30-day calendar workbook, and nine command-line tools in the bin directory that operationalise everything from scaffolding to the publish pack. A single operator can run the daily loop in roughly 60 to 90 minutes of active work per short, most of which is the human script-polish pass that the quality gates deliberately require."));

/* 2 ─ Current state */
bodyChildren.push(h1("2. Current State and Proven Foundations"));
bodyChildren.push(body("The dolphins pilot settled four questions that would otherwise be speculative. First, narration: VoiceStudio-style voice cloning was unavailable, so the pipeline adopted Edge-TTS with the en-GB-SoniaNeural voice, which matches the Myang persona and — crucially — emits WordBoundary events that give real word-level timestamps. Second, subtitle alignment: mega-shot originally estimated word timings by uniform distribution, which drifted visibly; the fix patches real Edge word timings into the narration metadata, after which subtitles and pen cues lock to the spoken word. Third, visuals: the huashu drawn-style grammar (y3_whiteboard) generates whiteboard clips in code, removing any dependency on stock footage or downloads. Fourth, encoding: the MS_ENCODER=x264 path produces a clean 1080x1920 H.264 file on CPU alone."));
bodyChildren.push(body("The pilot also surfaced operational quirks that the engine now treats as first-class constraints. Long-running xp jobs can be killed by sandbox watchdogs after they have already written valid artifacts; per-scene caches make re-runs cheap, so the render script simply retries each stage once. The xp narrate import loop stalls on a VoiceStudio availability ping in this environment, so the engine bypasses it by copying narration files directly and patching the metadata before rebuilding the timeline. These two workarounds are the difference between a demo that worked once and a system that survives repeated runs."));
bodyChildren.push(body("Finally, the mascot assets exist and are production-ready: a single shared vector rig renders six expressions plus a logo mark (unimpressed, squint, smug, shock, evidence-glasses, stamped), exported as PNG overlays with brand and puppet sheets. Chapter-card, corner-reaction, and end-stamp placements have all been mapped to concrete cue types in the pipeline, which Section 7 specifies."));

/* 3 ─ Goals & constraints */
bodyChildren.push(h1("3. Goals, Constraints, and Non-Goals"));
bodyChildren.push(body("The engine has three goals. The first is cadence: publish one short every day and one long-form every seventh day for 30 days without a missed slot, because faceless science channels live or die on upload consistency. The second is differentiation: every video must lead with a sourced, counter-intuitive fact and a drawn visual style, so that the feed test — one frame, no sound — is instantly recognisable as Myang Studio. The third is brand equity: Myang must accumulate familiarity across 26 shorts and 4 compilations while staying under strict cameo budgets, so that by day 30 the channel owns a character, not just a content style."));
bodyChildren.push(body("Constraints are fixed and non-negotiable. The voice is locked to en-GB-SoniaNeural at natural rate; changing voices mid-catalogue destroys audio brand consistency. The visual grammar is locked to y3_whiteboard with the box subtitle style. Loudness is locked to -14 LUFS with a one-dB tolerance. All facts must carry a verifiable source in the project research desk before they may reach narration, and AI-slop phrasing is banned outright by gate G1. On the non-goals side: the engine does not automate publishing (uploads remain a human click, deliberately), does not chase trend-jacking topics outside the niche, and does not generate facts from model memory without a source line."));

/* 4 ─ Architecture */
bodyChildren.push(h1("4. System Architecture"));
bodyChildren.push(body("The architecture adapts the six-stage loop popularised by open-source YouTube automation agents — research, script, production, review, publish, learn — onto the toolchain that the pilot actually proved. The table below maps each stage to its engine command and its human role. Two design decisions deserve emphasis. The topic bank is a single YAML file that drives everything downstream (the calendar workbook is generated from it), which eliminates the classic drift between a planning spreadsheet and the actual scripts. And the human pass is mandatory but narrow: the operator polishes narration and adds at_word cues, while facts, sources, voice, and style are locked by the scaffolder."));
bodyChildren.push(tblTitle("Table 1: Pipeline stages, commands, and the human role"));
bodyChildren.push(tbl(
  ["Stage", "Engine command", "Produces", "Human role"],
  [
    ["Research", "topics.yaml + nghien_cuu.md", "Sourced fact bank per topic", "Verify sources, extend bank"],
    ["Script", "new_video.py <slug>", "video.yaml scaffold + research desk", "Polish narration, add at_word cues"],
    ["Gate (pre)", "qa_gate.py --short", "G1+G2 pass before any render cost", "Read the report, fix flagged lines"],
    ["Production", "gen_narration.py, import_narration.py, render.sh", "Word-timed WAVs, timeline, art, mix, export", "None (retry on watchdog kills)"],
    ["Review", "qa_gate.py (full) + frame checks", "G1-G7 verdict, PASS required", "Spot-check frames, loudness"],
    ["Publish", "publish_pack.py --day N", "YouTube pack + social captions", "Upload, schedule, pin comment"],
    ["Learn", "Weekly review (Section 9)", "Retention notes, topic-bank edits", "Adjust hooks and formats"],
  ],
  [14, 30, 30, 26]
));
bodyChildren.push(body("Data flow is strictly one-directional: topics.yaml feeds the scaffolder, the scaffolder writes the project research desk, narration is generated only from polished yaml, and the render pipeline consumes only what those stages produced. Nothing downstream may invent content that a previous stage did not declare, which is what makes the quality gates enforceable rather than aspirational."));

/* 5 ─ 30-day plan */
bodyChildren.push(h1("5. The 30-Day Content Plan"));
bodyChildren.push(body("The month is organised into four weekly clusters plus a two-day tail, each cluster reinforcing one of four content pillars: survival engineering, senses and signals, records and extremes, and body hacks. Day 1 is the already-published dolphin pilot. Every short follows the same proven shape: a paradox hook inside the first three seconds, three sourced facts drawn as whiteboard beats, and an archivist outro that ends with the stamp. The full day-by-day calendar — dates, hooks, Myang beats, and statuses — ships in the companion workbook (30-day-content-calendar.xlsx), generated directly from the topic bank."));
bodyChildren.push(tblTitle("Table 2: Weekly clusters and long-form strategy"));
bodyChildren.push(tbl(
  ["Week", "Days", "Theme", "Daily shorts", "Long-form (day 7/14/21/28)"],
  [
    ["1", "1-7", "Survival engineering", "Dolphins (live), tardigrade, wood frog, mantis shrimp, mole rat, bowhead", "Animals that refuse to die (reuses days 2,3,5,6,13)"],
    ["2", "8-14", "Senses and signals", "Camel, platypus, peregrine, bee, squirrel, jellyfish", "Superpowers you can't see (reuses days 9,16,26,28,2)"],
    ["3", "15-21", "Records and extremes", "Pistol shrimp, octopus, giraffe, crow, shark, kangaroo rat", "The physics of record breakers (reuses days 4,10,15,14,21)"],
    ["4", "22-28", "Energy budgets", "Hummingbird, sperm whale, icefish, vulture, archerfish, axolotl", "Living on almost nothing (reuses days 8,20,29,21,12)"],
    ["5", "29-30", "Tail + review", "Sloth, flamingo", "Month-one retrospective (no render)"],
  ],
  [8, 10, 22, 32, 28]
));
bodyChildren.push(body("Long-form days replace the daily short rather than adding to it; the compilations are assembled by expanding the reused shorts' scene banks with connective narration, which means a 10-minute video costs roughly two hours of editing instead of a full research cycle. Instagram receives two to three reel cutdowns carved from each long-form, so the weekly posting surface is: seven vertical shorts, one horizontal long-form, and two to three reels. Every fact that enters a compilation must already exist in a research desk with a source; compilations may not introduce new claims."));

/* 6 ─ Anti-slop gates */
bodyChildren.push(h1("6. Anti-AI-Slop Quality Gates"));
bodyChildren.push(body("The gates exist because the failure mode of automated content is not technical — it is the slow drift toward generic, unsourced, over-promising filler that audiences and platforms have learned to punish. qa_gate.py runs seven checks and returns a binary verdict; a video that fails any gate does not publish, full stop. Gate G1 bans a curated list of slop phrases (dive into, unleash, mind-blowing, game-changer, buckle up, and similar) by regex over narration, subtitles, cues, and titles. Gate G2 requires every numbered fact in the research desk to carry a Source line, and warns when the only citation is Wikipedia. Gate G3 fails any scene whose word-timing metadata is empty — the exact signature of the uniform-distribution fallback that broke subtitle sync in the pilot — and requires 90 percent word coverage of the audio."));
bodyChildren.push(body("Gate G4 holds the mix within one decibel of -14 LUFS. Gate G5 holds duration inside the format window (45 to 120 seconds for shorts, 7 to 14 minutes for long-forms). Gate G6 enforces the Myang cameo budget described in Section 7. Gate G7 checks that a publish pack and social captions exist, so no video reaches upload day unwrapped. Beyond the automated gates, three editorial rules apply during the human pass: hooks must be a specific paradox rather than a generic promise; every scene must draw exactly one idea; and the outro must land the stamp cadence — three short declaratives, then the tagline."));
bodyChildren.push(tblTitle("Table 3: The seven gates"));
bodyChildren.push(tbl(
  ["Gate", "Checks", "Fail condition"],
  [
    ["G1", "Banned AI-slop phrases across script surfaces", "Any regex hit"],
    ["G2", "Evidence desk completeness", "Fact without a Source line; Wikipedia-only warning"],
    ["G3", "Word-level timing present and covering", "Empty check.tu; coverage below 90 percent"],
    ["G4", "Loudness", "Outside -15.0 to -13.0 LUFS"],
    ["G5", "Final duration", "Short outside 45-120 s; long outside 7-14 min"],
    ["G6", "Myang cameo budget", "More than 4 reactions; any reaction over 3 s"],
    ["G7", "Packaging", "Publish pack or captions missing"],
  ],
  [10, 45, 45]
));

/* 7 ─ Myang spec */
bodyChildren.push(h1("7. Myang Integration Specification"));
bodyChildren.push(body("Myang is the channel's answer to three business problems: a faceless channel needs a recognisable brand asset; platforms increasingly reward demonstrable originality; and retention benefits from a consistent visual ritual that viewers anticipate. The character is an original cream-plush archivist — emerald belt, FILE No. 001 lanyard, brass hand stamp, gold wire glasses — rendered from one shared vector rig, which guarantees that every appearance is geometrically identical across expressions. The persona is dry and perpetually unimpressed; the joke is that even miracles get filed. Sonia's deadpan delivery is cast to match, so voice and mascot reinforce one another."));
bodyChildren.push(figure("/home/z/my-project/download/myang/png/myang_logo.png", 170, 149));
bodyChildren.push(caption("Figure 1: Myang logo mark — cream plush, emerald accent, FILE No. 001 tag"));
bodyChildren.push(h2("7.1 Asset inventory"));
bodyChildren.push(tblTitle("Table 4: Expression assets and their sanctioned uses"));
bodyChildren.push(tbl(
  ["Asset", "Expression", "Sanctioned use"],
  [
    ["myang_unimused", "Half-lidded, flat mouth", "Default state; corner reactions on mild reveals"],
    ["myang_squint", "Suspicious side-eye", "Reactions at caveat or plot-turn moments"],
    ["myang_smug", "One-sided smirk", "Reactions where the animal outsmarts expectations"],
    ["myang_shock", "Wide-eyed alarm", "Reactions at the single biggest number in the video"],
    ["myang_evidence", "Gold glasses, inspecting", "Evidence beats; long-form chapter cards"],
    ["myang_stamped", "Stamp ceremony", "Outro only: FILED, then the tagline"],
    ["myang_logo", "Head-and-shoulders mark", "Avatars, watermark, thumbnail badge"],
  ],
  [22, 26, 52]
));
bodyChildren.push(figure("/home/z/my-project/download/myang/puppet_sheet.png", 260, 645));
bodyChildren.push(caption("Figure 2: Puppet sheet — one rig, six moods plus stamp and evidence poses"));
bodyChildren.push(h2("7.2 The four sanctioned appearances"));
bodyChildren.push(tblTitle("Table 5: Where Myang may appear"));
bodyChildren.push(tbl(
  ["Appearance", "Placement", "Hard rules"],
  [
    ["Chapter card", "Long-form section breaks", "Evidence pose; card carries chapter title and file number"],
    ["Evidence inspection", "One beat per short, on the key-fact moment", "Glasses on; Myang looks at the drawing, never at camera"],
    ["Corner reaction", "Up to 4 per video, max 3 s each", "Never over subtitles; never on serious welfare beats"],
    ["End stamp", "Final 2 s", "FILED stamp, then tagline: Filed under: beautiful — and lethal"],
  ],
  [20, 34, 46]
));
bodyChildren.push(body("The budget rules are the point of the design. Myang may never carry scene information, may not appear on footage of animal suffering, and spends roughly 90 percent of on-screen time unimpressed so that the occasional shock reaction reads as an event. Gate G6 turns the budget into an automated check; a video that over-uses the mascot fails review exactly as it would for a loudness miss. Overlays are PNGs with transparent margins and are placed by cue data in video.yaml, so placement is versioned with the script rather than improvised in an editor."));

/* 8 ─ Publishing ops */
bodyChildren.push(h1("8. Publishing Operations"));
bodyChildren.push(body("Publishing runs on a fixed daily rhythm. The render finishes the previous evening; the QA gate runs overnight on the final file; and the upload is scheduled for 06:00 local time, which places the video at the morning-commute and school-run peak. The publish pack generated by publish_pack.py contains three title candidates for A/B iteration, a description that leads with the hook and closes with the tagline, the tag set from the topic bank, an upload checklist, and a pinned-comment prompt that invites the audience to nominate the next file — a lightweight comments-driven research signal that feeds the weekly review."));
bodyChildren.push(body("Metadata discipline follows three rules. Titles state the paradox plainly and never promise emotion (no shocking, no insane — G1 applies to titles too). Descriptions carry the two-sentence drama summary and the trust line that names where the facts were checked, which is both honest and a soft differentiator in the science niche. The word-timed subtitle file is always uploaded as a caption track rather than burned in alone, because YouTube's search and the auto-translation layer both consume the track. Instagram reels reuse the same render with an alternate first-frame overlay and caption; the pack emits those captions per platform so the voice stays consistent everywhere."));
bodyChildren.push(body("Thumbnails for shorts are a single high-contrast frame from the whiteboard art with the logo badge; for long-forms, the thumbnail leads with the compilation title and the stamped-file motif. The pilot's thumbnail workflow (image generation, then the anh_bia config, then the thumbnail command) remains the reference implementation and is reproduced unchanged by render.sh when a thumbnail config is present."));

/* 9 ─ Learning loop */
bodyChildren.push(h1("9. Learning Loop and KPIs"));
bodyChildren.push(body("Every Sunday, the operator runs a 30-minute review that compares the week's videos against four numbers and converts findings into topic-bank edits for the following week. The loop borrows the evidence-first posture of the reference automation agents: no change is made on vibes, and every change is written down next to the number that justified it. The KPI targets below are deliberately modest for month one — the goal is to establish baselines, not to chase vanity thresholds before the catalogue is deep enough to matter."));
bodyChildren.push(tblTitle("Table 6: Month-one KPIs and the action each triggers"));
bodyChildren.push(tbl(
  ["Metric", "Month-one target", "If missed"],
  [
    ["Shorts retention at 100 percent view", "60 percent or better", "Tighten hook to first 2 s; cut scene count by one"],
    ["Swipe-away rate (first 3 s)", "Below 35 percent", "Re-cast hook paradox; test number-first hooks"],
    ["Long-form average view duration", "40 percent or better", "Move weakest chapter earlier; shorten chapters"],
    ["Myang-related comments", "Qualitative: mentions growing weekly", "Raise cameo budget by one reaction for one week only"],
    ["Upload consistency", "30 of 30 days", "Batch two renders per weekend as buffer"],
  ],
  [30, 28, 42]
));
bodyChildren.push(body("Two standing experiments run at low risk. First, hook style: number-led versus scenario-led, alternated across the week and compared on swipe-away rate. Second, outro stamp variant: plain FILED versus FILED plus audience prompt, compared on end-screen engagement. Both are logged in the weekly note with their sample sizes, and neither may change mid-week — the discipline of one variable at a time is what makes the results usable."));

/* 10 ─ Risks */
bodyChildren.push(h1("10. Risks and Mitigations"));
bodyChildren.push(body("The risk register is short on purpose; the engine's biggest structural risk is already mitigated by design decisions documented above. The remaining risks are operational and habitual, which is where a solo-run system usually breaks."));
bodyChildren.push(tblTitle("Table 7: Risk register"));
bodyChildren.push(tbl(
  ["Risk", "Likelihood", "Mitigation"],
  [
    ["Sandbox/machine reset loses tooling", "High", "bootstrap.sh restores clone, edge-tts, and assets in one command"],
    ["Watchdog kills during long renders", "Medium", "Per-scene caches + one retry per stage in render.sh"],
    ["Voice monotony across 26 shorts", "Medium", "Rate and pitch locked; variety comes from pacing and SFX, not voice drift"],
    ["Fact correction after publish", "Low", "Research desk is append-only; corrections ship as pinned-comment notes"],
    ["Mascot fatigue / over-exposure", "Medium", "G6 budget; quarterly review of cameo engagement"],
  ],
  [34, 14, 52]
));
bodyChildren.push(body("One risk is accepted rather than mitigated: the pipeline depends on a single TTS provider's voice id. If en-GB-SoniaNeural were retired, the engine would need a recast and a catalogue-wide note. The mitigation is documentation — the voice is declared in exactly one place, topics.yaml meta.voice — so a recast is a one-line change plus a conscious editorial decision rather than an archaeology project."));

/* 11 ─ Appendix */
bodyChildren.push(h1("11. Appendix A — Command Reference"));
bodyChildren.push(tblTitle("Table 8: Engine commands in run order"));
bodyChildren.push(tbl(
  ["Command", "Purpose"],
  [
    ["bash bin/bootstrap.sh", "Restore toolchain after reset (clone xp, install edge-tts)"],
    ["python3 bin/new_video.py <slug>", "Scaffold video.yaml + research desk from the topic bank"],
    ["python3 bin/qa_gate.py <proj> --short", "Pre-render script gate (G1, G2)"],
    ["python3 bin/gen_narration.py <proj>", "Edge-TTS narration + WordBoundary sidecars"],
    ["python3 bin/import_narration.py <proj>", "Copy WAVs, patch word timings, rebuild timeline"],
    ["bash bin/render.sh <proj>", "xp art, mix, render, export (x264 on CPU)"],
    ["python3 bin/qa_gate.py <proj> --short", "Full gate on the final export (G1-G7)"],
    ["python3 bin/publish_pack.py <proj> --day N", "YouTube pack + platform captions"],
    ["python3 bin/make_calendar.py", "Regenerate the calendar workbook from topics.yaml"],
  ],
  [40, 60]
));
bodyChildren.push(h1("12. Appendix B — Sandbox Survival Notes"));
bodyChildren.push(body("Four notes preserve the pilot's hard-won knowledge for future operators. Long xp jobs may be killed by watchdogs after writing valid artifacts; always re-run before diagnosing, because per-scene caches make the second attempt nearly free. The xp narrate import path stalls on a VoiceStudio availability ping in this environment; import_narration.py replaces it with a direct copy plus metadata patch, and this is now the standard route, not a workaround. The encoder is forced to x264 on CPU-only machines via MS_ENCODER; leave it unset on GPU machines to get the hardware path. When the built-in check command cannot finish, verify manually: extract frames with ffmpeg at key cue times and read the loudness graph with the ebur128 filter; the pilot's final file measured -14.0 LUFS this way."));
bodyChildren.push(body("A final note on the subtitle-timing chain, because it is the system's most valuable trick and the easiest to break: Edge-TTS emits WordBoundary offsets in hundreds of nanoseconds; the narration generator converts them to seconds; the importer writes them into each scene's check.tu array; and the timeline rebuild anchors every subtitle split and every at_word cue to those instants. Cue words must match displayed words exactly — the displayed token rise will never match a narrated rising, and a digit displayed as 4 must be quoted in the yaml. When a cue refuses to fire, the fix is almost always the displayed word, not the timing data."));

/* ══ DOCUMENT ═════════════════════════════════════════════════════════════ */
const doc = new Document({
  creator: "Z.ai",
  styles: {
    default: {
      document: {
        run: { font: { ascii: "Times New Roman", eastAsia: "SimSun" }, size: 24, color: "000000" },
        paragraph: { spacing: { line: 312 } },
      },
      heading1: {
        run: { font: { ascii: "Times New Roman", eastAsia: "SimHei" }, size: 32, bold: true, color: P.headText },
        paragraph: { spacing: { before: 360, after: 160, line: 312 }, outlineLevel: 0 },
      },
      heading2: {
        run: { font: { ascii: "Times New Roman", eastAsia: "SimHei" }, size: 28, bold: true, color: P.headText },
        paragraph: { spacing: { before: 240, after: 120, line: 312 }, outlineLevel: 1 },
      },
    },
  },
  sections: [
    { /* Section 1: cover — margin 0, no footer */
      properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 0, bottom: 0, left: 0, right: 0 } } },
      children: buildCoverR1({
        englishLabel: "MYANG STUDIO OPERATIONS",
        title: "30-Day Content Engine Playbook",
        subtitle: "Animal survival engineering · daily shorts · weekly long-forms · zero AI slop",
        metaLines: [
          "Channel: Myang Studio (faceless, archivist persona)",
          "Voice: en-GB-SoniaNeural — deadpan British, locked",
          "Pipeline: mega-shot xp + Edge-TTS word timing + whiteboard art",
          "Date: 28 October 2026",
        ],
        footerLeft: "Myang Studio", footerRight: "FILE No. 001 — OPERATIONS",
        palette: P,
      }),
    },
    { /* Section 2: TOC — Roman numerals */
      properties: {
        type: SectionType.NEXT_PAGE,
        page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1701, right: 1417 },
          pageNumbers: { start: 1, formatType: NumberFormat.UPPER_ROMAN } },
      },
      headers: { default: pageHeader() },
      footers: { default: romanFooter() },
      children: [
        new Paragraph({
          alignment: AlignmentType.CENTER, spacing: { before: 480, after: 360 },
          children: [new TextRun({ text: "Table of Contents", bold: true, size: 32, font: FH })],
        }),
        new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-2" }),
        new Paragraph({
          spacing: { before: 200 },
          children: [new TextRun({
            text: "Note: This Table of Contents is generated via field codes. To ensure page number accuracy after editing, please right-click the TOC and select \"Update Field.\"",
            italics: true, size: 18, color: "888888", font: F,
          })],
        }),
        /* body section starts with SectionType.NEXT_PAGE — no manual PageBreak here,
           a trailing break would create a blank page (postcheck rule ①) */
      ],
    },
    { /* Section 3: body — Arabic from 1 */
      properties: {
        type: SectionType.NEXT_PAGE,
        page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1701, right: 1417 },
          pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } },
      },
      headers: { default: pageHeader() },
      footers: { default: arabicFooter() },
      children: bodyChildren,
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("/home/z/my-project/download/content-engine/content-engine-playbook.docx", buf);
  console.log("OK content-engine-playbook.docx");
});
