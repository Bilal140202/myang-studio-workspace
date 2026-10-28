#!/usr/bin/env python3
"""Post-process playbook docx footers for WPS compatibility (per docx skill toc.md):
  - Roman footer (marker color 807F80): PAGE -> PAGE \\* ROMAN \\* MERGEFORMAT
  - Arabic footer (color 808080):       PAGE -> PAGE \\* arabic \\* MERGEFORMAT
  - Remove empty <w:pgNumType/> from document.xml (confuses WPS)
"""
import re, shutil, sys, zipfile

path = sys.argv[1]
tmp = path + ".tmp"

zin = zipfile.ZipFile(path)
zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    data = zin.read(item.filename)
    if re.match(r"word/footer\d+\.xml", item.filename):
        xml = data.decode("utf-8")
        if "PAGE" in xml:
            switch = "ROMAN" if "807F80" in xml else "arabic"
            xml2 = re.sub(r"(<w:instrText[^>]*>)\s*PAGE\s*(</w:instrText>)",
                          rf"\1 PAGE \\* {switch} \\* MERGEFORMAT \2", xml)
            if xml2 != xml:
                print(f"patched {item.filename} -> \\* {switch}")
            data = xml2.encode("utf-8")
    elif item.filename == "word/document.xml":
        xml = data.decode("utf-8")
        n = xml.count("<w:pgNumType/>")
        xml = xml.replace("<w:pgNumType/>", "")
        if n:
            print(f"removed {n} empty <w:pgNumType/> from document.xml")
        data = xml.encode("utf-8")
    zout.writestr(item, data)
zout.close(); zin.close()
shutil.move(tmp, path)
print("OK", path)
