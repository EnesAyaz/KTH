# Ayaz2026optical

**Tags: own-work**

**Design of a Pole-Changing Wound Field Synchronous Machine With Bipolar Optical Power Transfer Excitation** (2026), unpublished draft. no DOI

Access: local draft read (Airgap Harmonics/OPT-Workspace/source/original-draft.txt); not published (no Crossref/OpenAlex record found 2026-10-29).

- **Claim:** own-work (unpublished, IEEE Trans. Magn. draft, Ayaz/Tosun). Bipolar optical power transfer (OPT) excitation for a pole-changing WFSM.
- **Method:** Three stationary light sources: LS1 and LS2 are two bipolar channels (each has two rotor-mounted PV cell groups, selectively illuminated; the dark group gives a passive return path through its first cell and an external diode), LS3 feeds fixed-polarity groups. Unified PV model and corrected MPP matching condition feed the rotor winding design; 2D FEA.
- **Machine / inverter:** Rotor field coil groups LF1..LF4: LF1 and LF4 unipolar (LS3), LF2 and LF3 bipolar (LS1/LS2) reverse polarity between the 4-pole and 2-pole modes (the sign column of Table I is garbled in text extraction; the per-prior_work pattern is 4-pole [1 -1 1 -1] to 2-pole [1 1 -1 -1], i.e. the two middle groups flip). Stator: 36 slots, 48 turns/phase, winding factor 0.925; how the stator winding is reconnected for 4 vs 2 poles is not stated in the text read.
- **Power / voltage / speed numbers:** 10 kW, 4-pole 3000 rpm / 2-pole 6000 rpm, 400 V dc bus; stator current density 4.5 A/mm2, rotor 3.5 A/mm2; OD/ID 200/122 mm, stack 80 mm, airgap 0.5 mm; field current 12.5 A, 24 turns, R_f 0.093 ohm, 300 A-turns/pole; 30 W optical power per channel (PV V_MPP 2.4 V, I_MPP 12.5 A). FEA: 4-pole at 3000 rpm 822 W loss, 92.4 %; 2-pole at 6000 rpm 798 W, 93.1 %; stator copper 488 W both modes; OPT return-path loss 15.5 W per active phase.
- **Relevance to SPB:** Second own-work bipolar exciter and the scaling seed (10 kW draft) for the analyst; flagged draft, parameters unverified per its own open-questions file.
- **Limitations:** Unpublished, FEA only, 10 kW; the leader's notes list open issues (field resistance vs MPP matching, loss totals).
