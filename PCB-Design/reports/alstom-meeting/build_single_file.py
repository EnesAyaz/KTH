"""Build a single-file copy of the deck with every picture embedded as a data URI.

Usage:  python build_single_file.py
Output: SPB_status_update_single.html next to this script (works offline; fonts fall back without internet).
Pictures are stored once in a map; static <img> tags and pictures set later by the deck script
(timeline, roadmap, prototype tabs, header logos) are swapped to the embedded data.
"""
import base64
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "index.html")
OUT = os.path.join(HERE, "SPB_status_update_single.html")
IMG = os.path.join(HERE, "img")
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
BLANK = "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="

html = io.open(SRC, encoding="utf-8").read()

# every picture name the deck refers to, in HTML or in its script
names = sorted({n for n in re.findall(r"([A-Za-z0-9_\-]+\.(?:png|jpg|jpeg))", html) if os.path.exists(os.path.join(IMG, n))})
data = {}
for n in names:
    with open(os.path.join(IMG, n), "rb") as f:
        data[n] = "data:%s;base64,%s" % (MIME[os.path.splitext(n)[1].lower()], base64.b64encode(f.read()).decode("ascii"))

# static <img src="img/x"> -> placeholder + data-img, filled before first paint by the loader below
html, nstatic = re.subn(r'src="img/([A-Za-z0-9_\-]+\.(?:png|jpg|jpeg))"', lambda m: 'src="%s" data-img="%s"' % (BLANK, m.group(1)), html)

loader = """<script>
window.__IMGS=%s;
(function(){
  function fix(el){var s=el.getAttribute("data-img")||((el.getAttribute("src")||"").indexOf("img/")===0?el.getAttribute("src").slice(4):null);
    if(s&&window.__IMGS[s]&&el.getAttribute("src")!==window.__IMGS[s]){el.setAttribute("src",window.__IMGS[s]);el.removeAttribute("data-img")}}
  function scan(root){if(root.tagName==="IMG")fix(root);if(root.querySelectorAll)root.querySelectorAll("img").forEach(fix)}
  new MutationObserver(function(ms){ms.forEach(function(m){if(m.type==="attributes")fix(m.target);else m.addedNodes.forEach(function(n){if(n.nodeType===1)scan(n)})})})
    .observe(document.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:["src"]});
  document.addEventListener("DOMContentLoaded",function(){scan(document)});
})();
</script>
""" % json.dumps(data)

head = '<!doctype html>\n<html lang="en">\n<head>\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
html = head + html.replace("<style>", loader + "<style>", 1)
html = html.replace('<div id="stage">', "</head>\n<body>\n<div id=\"stage\">", 1) + "\n</body>\n</html>\n"
io.open(OUT, "w", encoding="utf-8").write(html)
print("pictures embedded: %d (%d static tags), file %.1f MB -> %s" % (len(data), nstatic, os.path.getsize(OUT) / 1e6, OUT))
