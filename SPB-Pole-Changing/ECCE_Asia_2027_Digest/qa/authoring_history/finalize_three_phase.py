from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'simulation/run_three_phase_codesign.py';s=p.read_text(encoding='utf-8')
s=s.replace("ax.text(.1,9.8,'(a) Three-wire SPB groups',fontsize=10)","ax.text(.1,9.8,'(a) Three-wire SPB groups',fontsize=10);ax.plot([1,1],[.7,8.7],color='black',lw=.9,zorder=0)")
s=s.replace("'Electromagnetic torque (N m)'","'Torque (N m)'").replace("'Electromagnetic power (kW)'","'Power (kW)'")
p.write_text(s,encoding='utf-8')
p=root/'build_digest.py';s=p.read_text(encoding='utf-8')
s=s.replace("D.core_properties.title='Co Design of Pole Changing Machines and Stacked Polyphase Bridges'","D.core_properties.title='Three Phase Stacked Bridge Drives for Pole Changing Hybrid Excited Machines'")
s=s.replace("'figures':3,'tables':2", "'figures':3,'tables':4")
s=s.replace("Thus an integer ratio r not divisible by three preserves balanced three-phase operation.","An integer ratio r not divisible by three preserves balanced three-phase operation.")
s=s.replace("A ratio divisible by three fails this construction; other winding families may differ [4].", "Thus 12/6 poles is supported, whereas 12/4 poles requires another winding family [4].")
s=s.replace("R=json.loads((ROOT/'simulation/results_three_phase/three_phase_codesign.json').read_text())", "R=json.loads((ROOT/'simulation/results_three_phase/three_phase_codesign.json').read_text())\nassert R['selected_winding']['Q']==72 and R['selected_winding']['N']==24\nassert R['metrics']['IPMSM 12 poles']['end_rpm_at_150kW']==4450\nassert R['metrics']['HEPM selectable 12 or 6']['end_rpm_at_300kW']==3300\nassert round(R['metrics']['HEPM selectable 12 or 6']['power_at_9000_kW'],2)==155.85, 'Update the manuscript numbers after changing model assumptions'")
p.write_text(s,encoding='utf-8')
