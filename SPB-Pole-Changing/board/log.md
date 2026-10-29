# Agent log

2026-10-29 15:47 | lit-scout | T02 | 01_literature/refs.bib, papers/*.md (42), gap_matrix.md, inputs_for_analyst.md | 42 refs (DOIs verified in Crossref), no traction WRSM pole-changing study found; IM EPC precedent strong
2026-10-29 15:4x | leader | T02 | check | 42/42 refs+notes, 0 unverified; WRSM-I_f finding relayed to analyst (T03): torque/A, kVA vs CPSR, cruise efficiency
2026-10-29 15:5x | leader | T02b | board/prior_work.md | Enes own work found: P1 WPT bipolar excitation letter, P2 PC-WFSM optical excitation (10 kW 4/2-pole FEA), P3 stator-harmonic excitation decks, P4 MMF transition; relayed to lit-scout and analyst
2026-10-29 15:59 | lit-scout | T02b | 01_literature/refs.bib (68 entries), papers/*.md (68), gap_matrix.md, inputs_for_analyst.md | added own-work P1 (published TIE 2026), P2 unpublished, 9 Peretti, 3 Bianchi/Padova, P1-reference pole-changing papers; WRSM gap revised
2026-10-29 16:0x | leader | T02b | check | 68/68 refs+notes; Ayaz2026primary DOI confirmed in Crossref (TIE 73(8) 12539-12544); P2 unpublished
2026-10-29 16:01 | analyst | T03 | 02_analytics/torque_speed_envelope.py, 02_analytics/results/torque_speed_envelope.json, 02_analytics/assumptions.md, 02_analytics/scratch/torque_speed_envelope_quicklook.png | IM 8->4 pole change: crossover 2090 rpm, CPSR 1.28->4.03, 332 vs 134 kW at 4500 rpm, cruise eta 97.05 % (2p8 cannot reach cruise); WRSM gains nothing from pole change (2p4 X_d up, I_ch 240->91 A), CPSR 8.1 at 2p8 with free I_d; PMSM CPSR >8.6; same 29.09 V / 310 A per leg
2026-10-29 16:02 | leader | T03 | check | done check passed; caveats: weak fixed-2p=8 IM baseline (CPSR 1.28) inflates IM gain; WRSM no-gain result hinges on L_m~k_w^2/p^2 scaling vs P2; 350 vs 300 kW open -> T03b + T04
2026-10-29 16:08 | leader | D02 | decision | Enes: 300 kW (SPB reference). T04 validates T03@350 kW as is; analyst reruns envelopes at 300 kW to a new file
2026-10-29 16:12 | leader | P5/D03 | board/prior_work.md, decisions.md | OPT repo reviewed: its own FEA study agrees WRSM pole change adds little range; its stator pole-change is the open item SPB fills. D03: hybrid-excited SM added
2026-10-29 16:18 | leader | D04 | data/vecto/ | VECTO LongHaul, RegionalDelivery, UrbanDelivery + segment/payload tables downloaded from code.europa.eu (stable 68a719e)
