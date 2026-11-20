import os,sys
SRC=r"C:\Github\KTH\PCB-Design\scripts\revb_flow_figures.py"
s=open(SRC,encoding="utf-8").read()
head=s.split("def rds(tj):")[0]
pan=s[s.index("def panel(ax, s):"):].split("\n\n")[0]
blk=s[s.index('LBP = os.path.join(ROOT, "simulation", "bb_q3d"'):s.index('    save(fig, "loop_breakdown")')]
R=[('"load-test board (no shunt)"','"load board (no shunt)"'),
   ('"top-row bypass 0805 per cell (+ 4 on the bottom)"','"top-row bypass 0805 per branch (+ 4 on the bottom)"'),
   ('"loop per cell (nH), Q3D"','"loop per branch (nH), Q3D"'),
   ('"loop inductance per cell (nH), mean of 4 cells"','"loop inductance per branch (nH), mean of 4 branches"'),
   ('ax.legend(loc="lower right", fontsize=8)','ax.legend(loc="center right", fontsize=8)')]
for a,b in R:
    assert blk.count(a)==1,a; blk=blk.replace(a,b)
blk+="    fig.savefig('C:/Github/KTH/PCB-Design/reports/infineon-meeting/img/loop_breakdown.png', dpi=220)\n    print('wrote')\n"
sys.argv=[SRC]; os.chdir(os.path.dirname(SRC))
g={"__file__":SRC,"__name__":"__main__"}
exec(compile(head+"\n"+pan+"\n\n"+blk,SRC,"exec"),g)
