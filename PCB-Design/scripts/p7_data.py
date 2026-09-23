"""Two individual low-side drain-current links for simultaneous sharing tests."""
from p6_data import *
parts=copy.deepcopy(parts)
OUT=ROOT/'hardware/epc2361-prototype-p7'
NAME='epc2361-prototype-p7'
for r in ['H1','H2']:parts.pop(r)
for pin in ['3','5','7']:parts['QL2']['pins'][pin]='D_QL2'
parts['TP12']['pins']['1']='D_QL2'
parts['LK2']=copy.deepcopy(parts['LK1'])
parts['LK2'].update(x=73,value='QL2 drain current link',pins={'1':'AC','2':'D_QL2'})
for r in ['LK1','LK2']:
    parts[r]['mpn']='CUSTOM-CU-LINK-P7'
    parts[r]['notes']='Matched formed copper current link, one per low-side device. 2mm wide x0.5mm thick, 6mm land pitch, 5mm underside rise. Hand solder. Coil closure/cable exit and parasitic matching require verification.'
