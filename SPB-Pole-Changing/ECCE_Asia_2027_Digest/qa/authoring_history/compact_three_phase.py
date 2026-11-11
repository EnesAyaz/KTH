from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'simulation/run_three_phase_codesign.py';s=p.read_text(encoding='utf-8-sig')
s=s.replace('ratings=[80,100,150,200,250,300,400,650]','ratings=[80,100,150,200,250,300,400,650,1200,1700]')
s=s.replace('for PH,PL in families:\n for N in Ns:','for PH,PL in families:\n for N in range(2,41):')
s=s.replace("figsize=(6.3,3.35)","figsize=(6.3,2.8)").replace("figsize=(6.3,3.65)","figsize=(6.3,3.0)").replace("figsize=(6.3,4.35)","figsize=(6.3,3.8)")
p.write_text(s,encoding='utf-8')
p=root/'build_digest.py';s=p.read_text(encoding='utf-8')
s=s.replace('sub_counter=0\ndef h(text):','sub_counter=0\npending_page=False\ndef h(text):').replace(' global sub_counter\n sub_counter=0\n x=p(text', ' global sub_counter,pending_page\n sub_counter=0\n x=p(text')
s=s.replace("x=p(text,'Heading 1',12,True);x.paragraph_format.space_before", "x=p(text,'Heading 1',12,True)\n if pending_page:x.paragraph_format.page_break_before=True;pending_page=False\n x.paragraph_format.space_before")
s=s.replace('def page():D.add_page_break()', 'def page():\n global pending_page\n pending_page=True')
s=s.replace("'explicit_page_breaks':4", "'heading_page_breaks':4")
s=s.replace('A ratio divisible by three fails this construction, without proving that every alternative winding is impossible.', 'A ratio divisible by three fails this construction; other winding families may differ [4].')
p.write_text(s,encoding='utf-8')
