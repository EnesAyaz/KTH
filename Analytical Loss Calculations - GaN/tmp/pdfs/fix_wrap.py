from pathlib import Path
p=Path('LOSS_MODELING.tex');s=p.read_text(encoding='utf-8');s=s.replace(r'''Piecewise-linear interpolation uses approximate readings of datasheet Figure 9 [1]:
$k_T=0.84,\ 1.00,\ 1.16,\ 1.33,\ 1.49,\ 1.65,\ 1.80$ at
$T_J=0,\ 25,\ 50,\ 75,\ 100,\ 125,\ 150$ $^\circ$C, respectively.''',r'''Piecewise-linear interpolation uses approximate readings of datasheet Figure 9 [1].
At 0, 25, 50, 75, 100, 125 and 150 $^\circ$C, the respective normalized factors are
0.84, 1.00, 1.16, 1.33, 1.49, 1.65 and 1.80.''');p.write_text(s,encoding='utf-8')
