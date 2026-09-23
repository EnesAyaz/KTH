"""Compact pin-array revision; P3 component data is preserved."""
from p3_data import *
parts=copy.deepcopy(parts)
OUT=ROOT/'hardware/epc2361-prototype-p4'
NAME='epc2361-prototype-p4'
for ref,x,y,angle,net in [('JDC1',8,10,90,'DC+'),('JDC2',8,17,90,'DC-'),('JAC1',78,22,0,'AC')]:
    c=parts[ref]
    c.update(x=x,y=y,angle=angle,value=net+' 24 pins',mpn='TSW-112-07-G-D',
             footprint='Connector_PinHeader_2.54mm:PinHeader_2x12_P2.54mm_Vertical',
             pins={str(i):net for i in range(1,25)},
             notes='24 parallel contacts. Full-array mating/thermal validation required; no single-pin current multiplication. Generic package model.')
