# Task board (leader edits; agents only read)

Status: todo | doing | done | blocked

| id | owner | status | inputs | output | acceptance check |
|---|---|---|---|---|---|
| T01 | leader | done | user brief | board/decisions.md: D01, D02 | D01 set by Enes; D02 provisional |
| T02 | lit-scout | done | CLAUDE.md | 01_literature/refs.bib, papers/*.md, gap_matrix.md | >=25 checked refs over 3 themes; gap matrix names >=3 gaps SPB fills |
| T02b | lit-scout | done | board/prior_work.md, Scholar | own-work + Bianchi + Peretti entries, revised gap_matrix.md | Enes papers tagged own-work; WRSM gap restated beyond P1-P3 |
| T03 | analyst | done | D01, D02 | 02_analytics/results/torque_speed_envelope.json | IM, PMSM, WRSM envelopes, each pole count; crossover speed; same SPB V/I limits for all |
| T04 | simulator | done (check FAILED: 59/136 >5 %) | T03 output | 03_simulation/results/*.json, validation.md | agrees with T03 within 5 % at 3 operating points |
| T03b | analyst | done | T03 results, review notes | 02_analytics/results/fair_baselines.json | fixed-pole IM baselines designed for their own pole count; T03 file left untouched |
| R01 | simulator -> analyst | doing | validation.md flags | data/machine_geometry.json (shared slot drawing), 03_simulation/reconcile_R01.md | one agreed slot geometry; IM slot leakage, flux caps and WRSM L_d/gap/tau_f consistent; analyst models re-run and agree within 5 %% at the T04 points |
| T05 | figure-maker | todo | T03, T04 results | 04_figures/torque_speed_envelope.* | reads only results JSON |
| T03d | analyst | done | VECTO data, literature | 02_analytics/results/drivetrain_losses.json | ratio-dependent gearbox loss + motor friction/windage law, each sourced; same model for every machine |
| T03c | analyst | done | inputs_for_analyst.md s7, Conto2022hybrid | 02_analytics/results/hesm_envelope.json, assumptions_hesm.md | HESM 8/4 pole at 300 kW, same SPB limits/gear rule as T03b; PM-share sweep; maps for T07 |
| T08 | analyst | doing | D05, T03b/T03c models, ../Analytical Loss Calculations - GaN | 02_analytics/results/module_count_sweep.json | for N = 2..24: feasible pole-count pairs per slot count, winding factors, device voltage class + inverter loss, start/CPSR/cruise for the best machine |
| T02d | lit-scout | done | T03d requests | refs + inputs_for_analyst.md s8 | sourced e-axle loss maps, EU 2017/2400 gear-loss values, helical mesh/churning data, measured traction-motor friction/windage, Bilgen/Saari/SKF refs |
| T07 | analyst | todo | T03b, T04, data/vecto | 02_analytics/results/drive_cycle.json | energy and loss per machine over VECTO LongHaul + RegionalDelivery; same driver model for all |
| G1-2 | lit-scout (2nd) | doing | H01-H08 | 01_literature/novelty_H*.md | closest papers + verdict per H; core-argument gap checked |
| G1-3 | analyst / simulator | doing | H01,H02,H04,H05 (T08), H06 (T04), H07 (T03c) | 02_analytics/results/screen_H*.json | metric vs fair baseline |
| G1-4 | gap-critic | todo | G1-2 + G1-3 | 06_reviews/H*_review.md | scores + kill argument per H |
| T06 | writer | todo | T02-T05 | 05_reports/weekly/2026-W44.md | every number traceable to a file |
