
ib=0.5;
ic=0.5;
db=0.5;
dc=0.5;

[theta_b_opt, theta_c_opt, min_rms] = optimize_interleaving_rms(ib, ic, db, dc)

min_rms = calculate_rms_no_shift(ib, ic, db, dc)