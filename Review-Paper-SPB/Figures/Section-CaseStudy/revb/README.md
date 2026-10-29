# Rev-B case-study update (28 October 2026)

Sources: C:/Github/KTH/PCB-Design/reports/slides/spb_revb_design_flow.pptx (latest deck), its data/*.json, and the user-provided poster_A0.svg and PCB/Q3D images.

The deck's summary line says 20 bank and 10 bypass parts per cell; detailed slides 16-19 establish 20 x 22 uF bank per LEG and 10 x 1 uF bypass per COMMUTATION CELL (four per leg). We use the detailed BOM: 480 uF nominal / 134.2 uF effective per leg; 1440 / 402.6 uF per three-phase SPB cell. Effective values: 6.35 uF per 22-uF part; 0.18 uF per 1-uF bypass. The ideal shared-bus ripple uses the switching-charge requirement from dclink_sizing.json, not its obsolete 1210 part counts/retention factors.

Loss/thermal screen: revb_flow_numbers.json npar/0.5nH/n=4, at cos(phi)=0.9, 50 kHz, 40 C ambient. This yields 18.0188 W/leg and 68.7548 C. The source's efficiency convention is 1-P_loss/6250 W; its 99.71% value is a semiconductor-only screen, not a measured or complete converter efficiency. Old copper/capacitor losses and PCB-area density are not retained because the final layout is different and those losses are pending.

Final loop extraction: final_numbers.json, not the older revb_numbers.json. Extracted DPT switching result: q3d_spice_numbers.json dpt, Rg_on=3.5 ohm, -1.9 V off. 92.9463 V is above the 90-V design target; it is not presented as passing. The load_rg3 run uses different gate assumptions and is not conflated with this DPT run.

The poster thermal diagram is a resistance-network estimate for the air-cooled load board, not Icepak validation. The shared cold plate is a separate machine-integration concept. No experimental result is claimed.

case_300kw.py regenerates the numerical macros and vector loss/sharing plots from these archived inputs. design_procedure.tex assembles Fig. 16. Figures/Exported/export_figures.py regenerates the embeddable PDF/PNG/SVG.
