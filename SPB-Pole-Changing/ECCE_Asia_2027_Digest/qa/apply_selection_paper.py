from pathlib import Path
root=Path(__file__).resolve().parent.parent
p=root/'build_digest.py';s=p.read_text(encoding='utf-8')
start=s.index("R=json.loads(");end=s.index('raw=REF.read_bytes()',start)
s=s[:start]+"R=json.loads((ROOT/'simulation/results_selection/design_selection.json').read_text())\nassert R['two_cell_control_example']['N']==2\nassert R['illustrative_selected_winding']['N']==12\nassert [d['N_voltage_min'] for d in R['device_classes']]==[20,14,10,6]\n"+s[end:]
start=s.index('# PAGE ONE');end=s.index('# Final controls',start)
s=s[:start]+(root/'qa/paper_selection_body.txt').read_text(encoding='utf-8-sig')+'\n'+s[end:]
start=s.index('def eq(text,num):');end=s.index('\ndef fig(',start)
s=s[:start]+'''def eq(text,num):
 x=D.add_paragraph();x.alignment=WD_ALIGN_PARAGRAPH.CENTER;x.paragraph_format.space_after=Pt(6)
 math=OxmlElement('m:oMath');r=OxmlElement('m:r');t=OxmlElement('m:t');t.text=text;r.append(t);math.append(r);x._p.append(math)
 rr=x.add_run('    ('+str(num)+')');rr.font.name='Times New Roman';rr.font.size=Pt(11)
 return x
''' +s[end:]
s=s.replace("D.core_properties.title='Three Phase Stacked Bridge Drives for Pole Changing Hybrid Excited Machines'","D.core_properties.title='Selecting Stacked Three Phase Cells and Pole Ratios for Traction Drives'")
s=s.replace("'figures':3,'tables':4", "'figures':4,'tables':3")
s=s.replace("'study':'three_wire_cell_count_and_pole_ratio'","'study':'discrete_device_slot_and_ratio_selection'")
p.write_text(s,encoding='utf-8')
