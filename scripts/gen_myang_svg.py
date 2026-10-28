#!/usr/bin/env python3
"""Myang SVG brand kit — one shared vector rig, 6 expressions + logo mark.
Rig: cream plush blob, bear ears, head seam tuft, half-lidded eyes, FILE № 001 lanyard
card, emerald belt, stubby limbs, brass hand stamp, gold wire glasses.
Outputs 6 SVGs + logo into /home/z/my-project/download/myang/svg/
"""
import os

OUT = "/home/z/my-project/download/myang/svg"

# ---- palette ----
CREAM   = "#F3EAD9"; CREAM_SH = "#E4D7BE"; CREAM_HI = "#FBF6EB"
INK     = "#2B2620"
EMERALD = "#0F6B4F"; EMER_D  = "#0A523C"
BRASS   = "#B08D57"; BRASS_D  = "#96754A"
GOLD    = "#C9A227"
CARD    = "#FAF5E8"
BLUSH   = "#E5A9A0"

def ell(cx, cy, rx, ry, fill, extra=""):
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" {extra}/>'

def path(d, fill, sw=7, extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'

def line(d, sw=7, col=None):
    return f'<path d="{d}" fill="none" stroke="{col or INK}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'

def body_rig():
    """Shared parts: legs, body blob, belt, ears, head, face plate, tag. Returns (parts, anchors)."""
    p = []
    # legs (stub) + feet
    p.append(path("M 400 700 C 398 760 396 790 396 820 C 396 845 380 858 362 858 C 344 858 332 844 334 820 L 338 706 Z", CREAM))
    p.append(path("M 624 700 C 626 760 628 790 628 820 C 628 845 644 858 662 858 C 680 858 692 844 690 820 L 686 706 Z", CREAM))
    p.append(ell(360, 838, 44, 26, CREAM_SH))
    p.append(ell(664, 838, 44, 26, CREAM_SH))
    # body blob (plush pear)
    p.append(path("M 300 470 C 300 380 372 330 512 330 C 652 330 724 380 724 470 C 724 590 700 706 512 706 C 324 706 300 590 300 470 Z", CREAM))
    # emerald belt
    p.append(path("M 322 560 C 380 596 644 596 702 560 C 706 584 704 606 700 620 C 620 656 404 656 324 620 C 320 606 318 584 322 560 Z", EMERALD))
    p.append(ell(512, 592, 92, 34, EMER_D))
    # ears (plush bear, behind head)
    p.append(ell(356, 172, 74, 70, CREAM))
    p.append(ell(668, 172, 74, 70, CREAM))
    p.append(ell(356, 174, 38, 36, "#DCBD92"))
    p.append(ell(668, 174, 38, 36, "#DCBD92"))
    # head (big plush round)
    p.append(path("M 268 262 C 268 130 372 62 512 62 C 652 62 756 130 756 262 C 756 372 654 434 512 434 C 370 434 268 372 268 262 Z", CREAM))
    # head seam tuft (top cap seam)
    p.append(path("M 366 96 C 440 66 584 66 658 96 C 660 118 654 136 646 148 C 560 118 464 118 378 148 C 370 136 364 118 366 96 Z", CREAM_SH))
    # tag (lanyard + card) — hangs from the neck, below the chin
    p.append(line("M 452 392 L 470 448", 8, EMERALD))
    p.append(line("M 572 392 L 554 448", 8, EMERALD))
    p.append(path("M 418 448 L 606 448 L 606 528 L 418 528 Z", CARD, 6))
    p.append(f'<rect x="496" y="440" width="32" height="16" rx="6" fill="{EMERALD}"/>')
    p.append(f'<text x="512" y="498" font-family="Noto Sans SC, Arial, sans-serif" font-size="30" font-weight="700" fill="{INK}" text-anchor="middle">FILE № 001</text>')
    return p

def eyes_unimused(x=0.0):
    """Signature half-lidded flat stare. x = head tilt offset for both eyes."""
    p = []
    for s in (-1, 1):
        ex = 512 + s * 88 + x
        p.append(ell(ex, 240, 34, 30, "#FFFFFF"))
        p.append(path(f"M {ex-34} 232 C {ex-12} 218 {ex+12} 218 {ex+34} 232", INK, 6))     # heavy lid
        p.append(ell(ex + 2, 248, 12, 14, INK))
        p.append(path(f"M {ex-26} 300 C {ex-8} 292 {ex+8} 292 {ex+26} 300", 4))            # lower lid crease
    return p

def brows(kind):
    p = []
    if kind == "flat":
        p.append(line("M 424 172 C 448 162 476 162 496 170", 9))
        p.append(line("M 528 170 C 548 162 576 162 600 172", 9))
    elif kind == "smug":   # one brow up (viewer right)
        p.append(line("M 424 176 C 448 168 476 168 496 176", 9))
        p.append(line("M 528 158 C 552 144 584 146 604 160", 9))
    elif kind == "shock":
        p.append(line("M 420 154 C 446 138 478 138 498 152", 9))
        p.append(line("M 526 152 C 546 138 578 138 604 154", 9))
    elif kind == "squint":
        p.append(line("M 424 160 C 450 172 478 172 498 162", 9))
        p.append(line("M 526 162 C 546 172 574 172 600 160", 9))
    elif kind == "soft":
        p.append(line("M 424 172 C 448 160 476 160 496 168", 9))
        p.append(line("M 528 168 C 548 160 576 160 600 172", 9))
    return p

def mouth(kind):
    if kind == "flat":    return line("M 462 330 C 488 334 536 334 562 330", 8)
    if kind == "smirk":   return line("M 456 326 C 490 344 546 338 574 314", 8)
    if kind == "o":       return ell(512, 336, 26, 34, "#5A1F1F") + ell(512, 348, 14, 12, "#E07A7A")
    if kind == "frown":   return line("M 458 344 C 486 324 538 324 566 344", 8)
    if kind == "smile":   return line("M 452 322 C 486 348 538 348 572 322", 8)
    if kind == "grin":    return (path("M 446 318 C 486 352 538 352 578 318 C 578 348 546 366 512 366 C 478 366 446 348 446 318 Z", "#5A1F1F", 7)
                                 + f'<path d="M 452 322 C 486 344 538 344 572 322 L 568 312 C 532 330 492 330 456 312 Z" fill="#FBF7EC"/>')
    return ""

def arms(kind):
    if kind == "down":
        return (path("M 312 470 C 282 520 268 560 262 596 C 258 620 272 634 290 632 C 310 630 318 616 322 592 C 328 556 334 520 340 486 Z", CREAM),
                path("M 712 470 C 742 520 756 560 762 596 C 766 620 752 634 734 632 C 714 630 706 616 702 592 C 696 556 690 520 684 486 Z", CREAM))
    if kind == "point":   # viewer-left arm points out
        return (path("M 322 470 C 250 452 200 444 156 442 C 134 441 126 456 132 470 C 138 484 152 488 174 490 C 220 494 272 500 330 510 Z", CREAM),
                path("M 712 470 C 742 520 756 560 762 596 C 766 620 752 634 734 632 C 714 630 706 616 702 592 C 696 556 690 520 684 486 Z", CREAM))
    if kind == "crossed": # stubby arms folded on belly
        return (path("M 316 480 C 350 520 420 548 500 552 L 620 552 C 660 550 688 528 690 500 C 660 540 590 556 508 552 C 420 548 350 522 316 480 Z", CREAM_SH),
                path("M 330 474 C 300 500 292 540 300 572 C 306 596 322 606 340 602 C 356 598 362 584 360 560 C 358 532 364 502 376 484 Z", CREAM))
    if kind == "up":      # right arm raised holding stamp
        return (path("M 312 470 C 282 520 268 560 262 596 C 258 620 272 634 290 632 C 310 630 318 616 322 592 C 328 556 334 520 340 486 Z", CREAM),
                path("M 700 470 C 736 420 756 360 762 300 C 764 276 750 264 732 268 C 714 272 706 286 700 310 C 686 368 668 428 650 478 Z", CREAM))
    return ("", "")

def stamp_prop():
    """Brass stamp held in the raised hand (arm 'up' → hand ~ (748, 296))."""
    p = []
    hx, hy = 736, 292
    p.append(f'<g transform="translate({hx},{hy}) rotate(14)">')
    p.append(path("M -16 0 C -16 60 -14 96 -14 128 C -14 150 2 162 18 162 C 34 162 46 150 46 128 L 44 0 Z", "#6B4A32"))  # wooden handle
    p.append(path("M -52 124 L 84 124 L 68 190 L -36 190 Z", BRASS))                                                     # brass neck
    p.append(path("M -70 188 C -70 172 -54 162 -2 162 C 50 162 66 172 66 188 C 66 208 50 218 -2 218 C -54 218 -70 208 -70 188 Z", BRASS))  # base
    p.append(ell(-2, 196, 40, 16, EMERALD))
    p.append('</g>')
    return p

def glasses_gold():
    p = []
    p.append(line("M 424 252 C 400 252 386 268 386 290 C 386 314 404 330 428 330 C 452 330 466 314 466 292 C 466 268 448 252 424 252", 7, GOLD))
    p.append(line("M 600 252 C 576 252 562 268 562 290 C 562 314 580 330 604 330 C 628 330 642 314 642 292 C 642 268 624 252 600 252", 7, GOLD))
    p.append(line("M 466 284 C 488 268 536 268 562 284", 7, GOLD))
    return p

def blush():
    return ell(394, 300, 34, 18, BLUSH, 'opacity="0.55"') + ell(630, 300, 34, 18, BLUSH, 'opacity="0.55"')

def svg_doc(inner, vb="0 0 1024 900"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="1024" height="900">'
            f'<g>{inner}</g></svg>')

def build(name, eye_kind, brow_kind, mouth_kind, arm_kind, glasses=False, stamp=False, blush_on=False, tilt=0):
    p = []
    aL, aR = arms(arm_kind)
    if arm_kind == "up":                     # raised arm behind, then stamp, then body over? — arm in front for grip
        p += [aL]
        p += body_rig()
        p += [aR] + stamp_prop()
    elif arm_kind == "crossed":
        p += body_rig() + [aL]
    else:
        p += body_rig() + [aL, aR]
    p += eyes(eye_kind) if not glasses else eyes(eye_kind) + glasses_gold()
    p += brows(brow_kind) + [mouth(mouth_kind)]
    if blush_on: p.append(blush())
    return svg_doc("".join(p))

def eyes(kind):
    if kind == "unimused": return eyes_unimused()
    if kind == "wide":     # shock
        p = []
        for s in (-1, 1):
            ex = 512 + s * 88
            p.append(ell(ex, 240, 40, 40, "#FFFFFF"))
            p.append(ell(ex, 244, 14, 16, INK))
            p.append(ell(ex - 6, 236, 5, 5, "#FFFFFF"))
        return p
    if kind == "focused":  # evidence: smaller, sharp
        p = []
        for s in (-1, 1):
            ex = 512 + s * 88
            p.append(ell(ex, 244, 32, 26, "#FFFFFF"))
            p.append(path(f"M {ex-32} 236 C {ex-10} 224 {ex+10} 224 {ex+32} 236", INK, 6))
            p.append(ell(ex + 2, 250, 11, 12, INK))
        return p
    return eyes_unimused()

SPECS = {
    "myang_unimused": dict(eye_kind="unimused", brow_kind="flat",   mouth_kind="flat",  arm_kind="down"),
    "myang_smug":     dict(eye_kind="unimused", brow_kind="smug",  mouth_kind="smirk", arm_kind="point"),
    "myang_shock":    dict(eye_kind="wide",     brow_kind="shock", mouth_kind="o",     arm_kind="down"),
    "myang_squint":   dict(eye_kind="unimused", brow_kind="squint",mouth_kind="frown", arm_kind="crossed"),
    "myang_evidence": dict(eye_kind="focused",  brow_kind="flat",  mouth_kind="flat",  arm_kind="point",  glasses=True),
    "myang_stamped":  dict(eye_kind="unimused", brow_kind="soft",  mouth_kind="smile", arm_kind="up",     stamp=True, blush_on=True),
    "myang_logo":     dict(eye_kind="unimused", brow_kind="flat",  mouth_kind="flat",  arm_kind="down"),
}

def build_logo():
    """Head-only mark: plush head + ears + face. Square canvas for avatars/stamps."""
    p = []
    p.append(ell(356, 470, 92, 86, CREAM)); p.append(ell(668, 470, 92, 86, CREAM))
    p.append(ell(356, 472, 44, 42, "#DCBD92")); p.append(ell(668, 472, 44, 42, "#DCBD92"))
    p.append(path("M 200 640 C 200 420 340 320 512 320 C 684 320 824 420 824 640 C 824 810 686 896 512 896 C 338 896 200 810 200 640 Z", CREAM))
    p.append(path("M 316 372 C 420 320 604 320 708 372 C 710 402 700 428 688 444 C 576 400 448 400 336 444 C 324 428 314 402 316 372 Z", CREAM_SH))
    # face features are tuned for the body rig (head center ~y 248); shift down to the logo head center (y 608)
    p.append('<g transform="translate(0,360)">' + "".join(eyes_unimused() + brows("flat") + [mouth("flat")]) + '</g>')
    # emerald identity ring
    p.append(f'<circle cx="512" cy="608" r="468" fill="none" stroke="{EMERALD}" stroke-width="26"/>')
    return svg_doc("".join(p), vb="0 0 1024 1024")

def main():
    os.makedirs(OUT, exist_ok=True)
    for name, kw in SPECS.items():
        if name == "myang_logo":
            doc = build_logo()
        else:
            doc = build(name, **kw)
        fp = os.path.join(OUT, name + ".svg")
        open(fp, "w").write(doc)
        print("SVG", fp)

if __name__ == "__main__":
    main()
