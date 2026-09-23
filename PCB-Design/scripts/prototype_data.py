"""Authoritative component and net list for the four-FET prototype."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'hardware/epc2361-prototype'
NAME='epc2361-prototype';LIB=NAME
parts={}
def add(ref,value,mpn,fp,pins,x,y,angle=0,dnp=False,notes=''):
    parts[ref]=dict(value=value,mpn=mpn,footprint=fp,pins={str(k):v for k,v in pins.items()},x=x,y=y,angle=angle,dnp=dnp,notes=notes)
for ref,x,y,ang,gate,drain,source in [('QH1',34,38,180,'GH1','DC+','AC'),('QL1',34,32,180,'GL1','AC','DC-'),('QH2',56,32,0,'GH2','DC+','AC'),('QL2',56,38,0,'GL2','AC','DC-')]:
    add(ref,'EPC2361','EPC2361',LIB+':EPC2361',{1:gate,2:source,3:drain,4:source,5:drain,6:source,7:drain},x,y,ang)
for j,x in enumerate([50.75,52.85,54.95,57.05,59.15,61.25],1):
    add('C'+str(j),'1u 100V','C2012X7S2A105K125AB','Capacitor_SMD:C_0805_2012Metric',{1:'DC+',2:'DC-'},x,26,90)
for j,x in enumerate([39.25,37.15,35.05,32.95,30.85,28.75],7):
    add('C'+str(j),'1u 100V','C2012X7S2A105K125AB','Capacitor_SMD:C_0805_2012Metric',{1:'DC+',2:'DC-'},x,44,270)
for ref,x,y,gate,drive,ang in [('RGH1',38.3,39.23,'GH1','HO',180),('RGL1',38.3,33.23,'GL1','LO',180),('RGH2',51.7,30.77,'GH2','HO',0),('RGL2',51.7,36.77,'GL2','LO',0)]:
    add(ref,'0R tune','RC0402JR-070RL','Resistor_SMD:R_0402_1005Metric',{1:drive,2:gate},x,y,ang,notes='Individual gate damping footprint. Tune during double-pulse testing.')
for ref,x,y,gate,source,ang in [('JGH1',40.95,39.23,'GH1','AC',180),('JGL1',40.95,33.23,'GL1','DC-',180),('JGH2',49.05,30.77,'GH2','AC',0),('JGL2',49.05,36.77,'GL2','DC-',0)]:
    add(ref,'G / KS','FTS-102-01-L-S','Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical',{1:gate,2:source},x,y,ang,notes='Measurement/external-drive header; never connect a second active driver. Remove local series resistor to isolate onboard output. Generic footprint: verify manufacturer drawing before release.')
for ref,x,y,net in [('JDC1',75,15,'DC+'),('JDC2',75,31,'DC-'),('JAC1',75,49,'AC')]:
    add(ref,net+' M4','74650094','TerminalBlock_Wuerth:Wuerth_REDCUBE-THR_WP-THRBU_74650094_THR',{1:net},x,y,notes='85 A maximum at20C is terminal-only; assembly/current path requires validation. 1.2Nm maximum specified torque.')
add('U1','LMG1210','LMG1210RVRR',LIB+':LMG1210_RVR',{1:'NC1',2:'VIN',3:'DC-',4:'VDD',5:'DC-',6:'VDD',7:'DC-',8:'LO',9:'AC',10:'HO',11:'NC11',12:'HB',13:'AC',14:'AC',15:'NC15',16:'AC',17:'BST',18:'HI',19:'LI',20:'DC-',21:'AC'},45,35,notes='IIM: external nonoverlapping HI/LI; no internal shoot-through interlock in this mode.')
add('JCTRL1','12V / GND / HI / GND / LI / GND','TSW-106-07-G-S','Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical',{1:'VIN',2:'DC-',3:'HI',4:'DC-',5:'LI',6:'DC-'},15,24)
for ref,val,mpn,fp,pins,x,y,ang in [
 ('C13','1u 35V','C1608X7R1V105K080AC','C_0603_1608Metric',{1:'VIN',2:'DC-'},39,24,0),
 ('C14','10u 25V','C2012X5R1E106K125AB','C_0805_2012Metric',{1:'VDD',2:'DC-'},44,44.5,90),
 ('C15','10u 25V','C2012X5R1E106K125AB','C_0805_2012Metric',{1:'VDD',2:'DC-'},47,44.5,90),
 ('C16','100n 50V','C1608X7R1H104K080AA','C_0603_1608Metric',{1:'VDD',2:'DC-'},44,39.5,90),
 ('C17','1u 16V','C1608X7R1C105K080AC','C_0603_1608Metric',{1:'HB',2:'AC'},47,27.8,90),
 ('C18','100n 50V','C1608X7R1H104K080AA','C_0603_1608Metric',{1:'HB',2:'AC'},45,31.3,0)]:
    add(ref,val,mpn,'Capacitor_SMD:'+fp,pins,x,y,ang,notes='Verify effective capacitance and temperature; VDD X5R parts rated85C.')
add('RB1','2.2R','RC0603FR-072R2L','Resistor_SMD:R_0603_1608Metric',{1:'BST',2:'BST_A'},44,27.5,90)
add('D1','BAS21H','BAS21H,115','Diode_SMD:D_SOD-123F',{1:'HB',2:'BST_A'},47,24,0,notes='External bootstrap diode: cathode HB, anode BST_A. Not a bootstrap voltage clamp.')
for ref,x,net in [('RH1',36,'HI'),('RL1',39,'LI')]:add(ref,'10k','RC0402FR-0710KL','Resistor_SMD:R_0402_1005Metric',{1:net,2:'DC-'},x,21,90)
for ref,x,y,net in [('TP1',63,28,'DC+'),('TP2',33,25,'DC-'),('TP3',25,35,'AC'),('TP4',47,22,'HB'),('TP5',51,46,'VDD')]:
    add(ref,net,'PCB copper test pad',LIB+':Probe_Pad',{1:net},x,y,notes='PCB feature; no purchased component.')
