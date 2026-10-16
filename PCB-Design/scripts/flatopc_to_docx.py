"""
Flat OPC (Word XML, one file) -> .docx package, without Word.

    python scripts/flatopc_to_docx.py <in.xml> <out.docx>

Used by the ICPE digest build when Word's own SaveAs2 of the Flat OPC file fails (stage 2, export_icpe_digest.ps1).
The part XML is copied as raw text: re-serialising it would rename namespace prefixes that mc:Ignorable refers to.
"""
import base64
import re
import sys
import zipfile

src, dst = sys.argv[1], sys.argv[2]
txt = open(src, encoding="utf-8").read()
parts, types = [], {}
for m in re.finditer(r'<pkg:part\b([^>]*)>(.*?)</pkg:part>', txt, re.S):
    attrs, body = m.group(1), m.group(2)
    name = re.search(r'pkg:name="([^"]+)"', attrs).group(1)
    types[name] = re.search(r'pkg:contentType="([^"]+)"', attrs).group(1)
    x = re.search(r'<pkg:xmlData([^>]*)>(.*)</pkg:xmlData>', body, re.S)
    if x:
        sa = "no" if 'originalXmlStandalone="no"' in x.group(1) else "yes"
        data = ('<?xml version="1.0" encoding="UTF-8" standalone="%s"?>\r\n' % sa + x.group(2).strip()).encode("utf-8")
    else:
        b = re.search(r'<pkg:binaryData[^>]*>(.*)</pkg:binaryData>', body, re.S).group(1)
        data = base64.b64decode("".join(b.split()))
    parts.append((name.lstrip("/"), data))

ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
      '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">']
ct += ['<Override PartName="%s" ContentType="%s"/>' % (n, c) for n, c in sorted(types.items())]
ct.append("</Types>")
with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", "".join(ct))
    for name, data in parts:
        z.writestr(name, data)
print("wrote", dst, len(parts), "parts")
