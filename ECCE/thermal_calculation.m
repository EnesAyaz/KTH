% 2Level 3 Phase

Die_area=300;

r_jc_eq= 2.5/Die_area/6;

r_ch_eq= 0.025/3;


P_loss= ((300/0.994)-300)*1e3
DeltaT=75;

r_tot= DeltaT/ P_loss;
 rha=r_tot-r_jc_eq-r_ch_eq;

[r_jc_eq, r_ch_eq, rha]


CSPI=10;
1/CSPI/rha

%%  2Level 6 Phase

Die_area=120;

r_jc_eq= 2.5/Die_area/12;

r_ch_eq= 0.025/6;


P_loss= ((300/0.994)-300)*1e3
DeltaT=75;

r_tot= DeltaT/ P_loss;
 rha=r_tot-r_jc_eq-r_ch_eq;
%
[r_jc_eq, r_ch_eq, rha]


CSPI=10;
1/CSPI/rha

%%  3Level 

Die_area=90;

r_jc_eq= 2.5/Die_area/18;

r_ch_eq= 0.025/9;


P_loss= ((300/0.994)-300)*1e3
DeltaT=75;

r_tot= DeltaT/ P_loss;
 rha=r_tot-r_jc_eq-r_ch_eq;
%
[r_jc_eq, r_ch_eq, rha]

CSPI=10;
1/CSPI/rha
