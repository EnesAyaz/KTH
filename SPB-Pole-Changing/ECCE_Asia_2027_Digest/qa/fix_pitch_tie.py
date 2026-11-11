from pathlib import Path
p=Path(__file__).resolve().parent.parent/'simulation/run_design_selection.py';s=p.read_text(encoding='utf-8-sig');s=s.replace("j=int(np.argmax(score));y=int(ys[j]);short=", "j=int(np.flatnonzero(score>=score.max()-1e-10)[0]);y=int(ys[j]);short=")
p.write_text(s,encoding='utf-8')

