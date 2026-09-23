from prototype_data import *
import copy
parts=copy.deepcopy(parts)
OUT=ROOT/'hardware/epc2361-prototype-p3'
NAME='epc2361-prototype-p3'
# Retain local custom footprint library nickname.
left={'QH1','QL1','RGH1','RGL1','JGH1','JGL1'}|{'C'+str(i) for i in range(7,13)}
right={'QH2','QL2','RGH2','RGL2','JGH2','JGL2'}|{'C'+str(i) for i in range(1,7)}
for r,c in parts.items():
    if r in left:c['x']+=14
    elif r in right:c['x']+=10
    elif r not in {'JDC1','JDC2','JAC1','JCTRL1','TP1','TP2','TP3'}:c['x']-=9
for r,x,y in [('JDC1',14,13),('JDC2',30,13),('JAC1',80,35),('JCTRL1',12,30),('TP1',73,28),('TP2',44,20),('TP3',74,43)]:parts[r]['x']=x;parts[r]['y']=y

parts['TP5']['x']=39;parts['TP5']['y']=49

# Both parallel cells face the driver on the left.
for ref,x,y in [('QH1',48,32),('QL1',48,38),('RGH1',43.7,30.77),('RGL1',43.7,36.77),('JGH1',41.05,30.77),('JGL1',41.05,36.77)]:
    parts[ref]['x']=x;parts[ref]['y']=y;parts[ref]['angle']=0
for i in range(7,13):parts['C'+str(i)]['angle']=90

# Symmetric six-capacitor fast banks above each pair; lower banks supplementary.
for j in range(6):
    c=copy.deepcopy(parts['C'+str(j+1)]);c['x']-=18;parts['C'+str(19+j)]=c
    c=copy.deepcopy(parts['C'+str(7+j)]);c['x']+=18;parts['C'+str(25+j)]=c
bus_caps=['C'+str(i) for i in list(range(1,13))+list(range(19,31))]

