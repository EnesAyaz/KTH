import os,re,subprocess
from concurrent.futures import ThreadPoolExecutor
SP=os.path.abspath("pdf")
src=open(r"C:\Github\KTH\PCB-Design\reports\infineon-meeting\SPB_GaN_Infineon_embedded.html",encoding="utf-8").read()
css='<style>#nav{display:none!important}#stage{padding:0!important}#canvas{transform:none!important;left:0!important;top:0!important}.slide{border:0!important;border-radius:0!important}</style>'
src=src+css
open(os.path.join(SP,"p.html"),"w",encoding="utf-8").write(src)
ids=re.findall(r'<section class="slide[^"]*" id="([^"]+)"',src)
E=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
def shot(a):
    i,sid=a; out=os.path.join(SP,"%02d.png"%(i+1))
    if os.path.exists(out): os.remove(out)
    for _ in range(3):
        subprocess.run([E,"--headless=new","--disable-gpu","--hide-scrollbars","--force-device-scale-factor=2","--user-data-dir="+SP+r"\u%d"%(i%4),
          "--window-size=1280,720","--virtual-time-budget=4000","--screenshot="+out,"file:///"+SP.replace("\\","/")+"/p.html#"+sid],capture_output=True,timeout=120)
        if os.path.exists(out): return
with ThreadPoolExecutor(4) as ex: list(ex.map(shot,enumerate(ids)))
print(len(ids),"slides",len([f for f in os.listdir(SP) if f.endswith(".png")]),"pngs")
