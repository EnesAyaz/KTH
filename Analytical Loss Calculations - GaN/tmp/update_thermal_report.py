from pathlib import Path
p=Path('test_loss_model.py');s=p.read_text(encoding='utf-8').replace("self.assertAlmostEqual(r['junction_temperature'],expected,places=6)","self.assertAlmostEqual(r['junction_temperature'],expected,delta=1e-6)");p.write_text(s,encoding='utf-8')
p=Path('LOSS_MODELING.tex');s=p.read_text(encoding='utf-8-sig').replace('\\usepackage[T1]{fontenc}\n','')
a=s.index('\\textbf{Temperature is included');b=s.index('\n\\newpage',a)
s=s[:a]+r'''The default \texttt{rds\_temperature\_mode=iterative} couples conduction loss to
junction temperature. The maximum 25 $^\circ$C resistance, 1.0 m$\Omega$, is selected
by default. At each iteration the normalized datasheet curve gives
\begin{align*}
 R_{\rm DS,on}(T_J)&=R_{\rm DS,on,25}\,k_T(T_J),\\
 d_{\rm dead}&=2t_{\rm dead,eff}f_{\rm sw}=0.01,\\
 P_{\rm cond}(T_J)&=I_{\rm rms}^{2}k_{\rm wf}^{2}R_{\rm DS,on}(T_J)(1-d_{\rm dead}),\\
 T_J^{(n+1)}&=T_{\rm ref}+\frac{R_\theta}{2}
 [P_{\rm cond}(T_J^{(n)})+P_{\rm overlap}+P_{\rm COSS}+P_{\rm dead}].
\end{align*}
The code starts at the selected case or ambient temperature and repeats until the
thermal residual is below $10^{-6}$ $^\circ$C, with a maximum of 200 iterations.
This numerical tolerance does not imply equivalent physical accuracy.

Piecewise-linear interpolation uses approximate readings of datasheet Figure 9 [1]:
$k_T=0.84,\ 1.00,\ 1.16,\ 1.33,\ 1.49,\ 1.65,\ 1.80$ at
$T_J=0,\ 25,\ 50,\ 75,\ 100,\ 125,\ 150$ $^\circ$C, respectively.
The typical normalized curve scales the selected typical or maximum 25 $^\circ$C
resistance; it is not a guaranteed hot-resistance limit. No extrapolation is made
outside 0--150 $^\circ$C. Leaving that range or failing to converge produces an
explicit error instead of a reported steady-state solution.

The converged defaults are \textbf{$T_J=50.4922$ $^\circ$C},
\textbf{$R_{\rm DS,on}=1.16335$ m$\Omega$}, and $P_{\rm cond}=1.84274$ W
for both FETs combined. The small dead-time correction avoids double counting
normal conduction during reverse-conduction intervals. Optional external loop loss
is $P_{\rm loop}=I_{\rm rms}^{2}k_{\rm wf}^{2}R_{\rm loop}$.

Manual mode remains available and uses the entered multiplier (default 1.7) without
feedback. Iterative mode ignores that manual multiplier. The result reports updated
resistance, junction temperature, iteration count and residual. It estimates
steady-state temperature under the specified cooling conditions; it does not measure
actual junction temperature.
'''+s[b:]
s=s.replace('5.8005','4.9505').replace('99.4561','99.5354').replace('2.8862','2.46114').replace('50.5772','50.4922')
s=s.replace('The resistance multiplier remains 1.7 even though the case-based estimate is near\n51 $^\\circ$C; there is no automatic temperature feedback.', 'Conduction loss is recomputed with the converged resistance. The other loss terms\nremain fixed during iteration; temperature dependence of gate charge, reverse drop\nand switching energy is not modeled.')
s=s.replace('Seven numerical checks cover loss accounting, waveform integration,\ninput handling and thermal-loss separation.', 'Ten numerical checks cover loss accounting, waveform integration, input handling,\nthermal balance, an independent closed-form solution and failure conditions.')
p.write_text(s,encoding='utf-8')
p=Path('LOSS_MODELING.md');s=p.read_text(encoding='utf-8')
s=s.replace('and RDS temperature multiplier 1.7.', 'and iterative RDS temperature feedback. Manual mode retains a 1.7 multiplier.')
s=s.replace('The 1.7 RDS factor is a retained conservative assumption corresponding roughly to 115 C, not iterated from the reported junction temperature.', 'Iterative mode interpolates the normalized RDS curve from Figure 9 at the calculated junction temperature. Manual mode retains the optional fixed multiplier 1.7.')
a=s.index('## Stress, thermal, and limitations')
s=s[:a]+'''## Iterative junction temperature and on-resistance

Default `rds_temperature_mode="iterative"` solves the coupled steady-state conduction/thermal problem. Approximate Figure 9 readings are normalized factors 0.84, 1.00, 1.16, 1.33, 1.49, 1.65, 1.80 at 0, 25, 50, 75, 100, 125, 150 C. Piecewise-linear interpolation scales the selected 25 C typical/maximum resistance. These are approximate typical curve readings, not guaranteed hot-resistance specifications.

Starting at the selected case/ambient temperature, each iteration updates RDS(T), conduction loss and semiconductor loss, then evaluates `Tnext = Tref + Rtheta * Psemiconductor(T)/2`. It stops when the thermal residual is below 1e-6 C, with at most 200 iterations. The code raises an explicit error on nonconvergence or temperatures outside the curve's 0..150 C range; it does not clamp or extrapolate into an invalid steady-state result.

The outputs include `junction_temperature`, `rds_on_mohm`, `rds_on_ohm`, `rds_temperature_factor`, `thermal_iterations` and `thermal_residual_c`. With the default maintained case temperature of 50 C: Tj is 50.4922 C, RDS(on) is 1.16335 mOhm, conduction loss is 1.84274 W, and total loss is 4.95047 W. The solution estimates steady-state temperature under the supplied cooling assumptions, not measured real junction temperature. Other loss terms remain fixed during this iteration.

Set `rds_temperature_mode="manual"` to recover the fixed `rds_temp_scale` approach. That multiplier is ignored in iterative mode. The GUI displays the temperature and updated resistance prominently.

'''+s[a:]
s=s.replace('The legacy TeX/PDF report has not been regenerated.', 'The TeX/PDF report includes the iterative solution, current waveform graphic, and revised default results, without a table of contents or paralleling section.')
p.write_text(s,encoding='utf-8')
p=Path('README.md');s=p.read_text(encoding='utf-8');s=s.replace('The pre-existing `LOSS_MODELING.tex` and `LOSS_MODELING.pdf` are legacy snapshots and have not been regenerated; use the Markdown documentation for the updated model.', 'The updated `LOSS_MODELING.tex` and `LOSS_MODELING.pdf` document the current model without a table of contents or a paralleling section.')
s+='\nThe default iterative thermal mode updates RDS(on) from the datasheet temperature curve until thermal balance converges. The GUI reports Tj and updated RDS(on). Default case-mode results: 50.4922 C, 1.16335 mOhm, and 4.95047 W total loss. Select manual RDS mode to use the fixed multiplier instead. The solver rejects temperatures outside the supported 0..150 C curve and reports nonconvergence explicitly.\n'
p.write_text(s,encoding='utf-8')
