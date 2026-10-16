"""
Blind review: blank author / last-modified-by / company / title in a .docx (Word writes the user name on save).
    python scripts/clean_docx_meta.py file.docx
"""
import os
import re
import shutil
import sys
import tempfile
import zipfile

FIELDS = {"docProps/core.xml": ["dc:creator", "cp:lastModifiedBy", "dc:title", "dc:subject", "cp:keywords",
                                "dc:description"],
          "docProps/app.xml": ["Company", "Manager"]}


def clean(path):
    tmp = tempfile.mktemp(suffix=".docx", dir=os.path.dirname(path))
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename in FIELDS:
                t = data.decode("utf-8")
                for tag in FIELDS[item.filename]:
                    t = re.sub(r"<%s>[^<]*</%s>" % (tag, tag), "<%s></%s>" % (tag, tag), t)
                data = t.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(tmp, path)
    print("metadata cleared:", path)


if __name__ == "__main__":
    clean(sys.argv[1])
