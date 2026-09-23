"""P6: individual low-side drain-current link. Fit remains under review."""
from p5_data import *
parts=copy.deepcopy(parts)
OUT=ROOT/'hardware/epc2361-prototype-p6'
NAME='epc2361-prototype-p6'
for pin in ['3','5','7']:parts['QL1']['pins'][pin]='D_QL1'
parts['TP8']['pins']['1']='D_QL1'
parts['LK1']=dict(value='QL1 drain current link',mpn='CUSTOM-CU-LINK-P6',
    footprint=LIB+':Current_Link',pins={'1':'AC','2':'D_QL1'},
    x=55,y=35,angle=0,dnp=False,
    notes='Sole QL1 drain-current path. Provisional formed copper 2mm wide x0.5mm thick, 6mm land pitch, 3mm underside rise. Hand solder, no paste. Exact PEM coil fit and link temperature/inductance require verification; not a generic jumper.')
