#!/usr/bin/env python3
"""Rasterize Myang SVGs to transparent PNGs (playwright screenshot) + build contact sheet (PIL)."""
import glob, os
from playwright.sync_api import sync_playwright

SVG_DIR = "/home/z/my-project/download/myang/svg"
PNG_DIR = "/home/z/my-project/download/myang/png"

def main():
    os.makedirs(PNG_DIR, exist_ok=True)
    svgs = sorted(glob.glob(os.path.join(SVG_DIR, "*.svg")))
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=["--no-sandbox"])
        for fp in svgs:
            name = os.path.splitext(os.path.basename(fp))[0]
            pg = b.new_page(viewport={"width": 1024, "height": 1024}, device_scale_factor=2)
            pg.goto("file://" + fp)
            el = pg.query_selector("svg")
            el.screenshot(path=os.path.join(PNG_DIR, name + ".png"), omit_background=True)
            pg.close()
            print("PNG", name)
        b.close()

if __name__ == "__main__":
    main()
