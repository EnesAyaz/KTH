# Manuscript figure style

Applied to the 15 active manuscript figures, including the retained conceptual spider graph.

Visual references inspected:
- Rohner, Huber, Miric and Kolar, Electronics 2024, 13, 1259: attached version, especially Figs. 2, 3, 5 and 8. https://www.pes-publications.ee.ethz.ch/uploads/tx_ethpublications/user_upload/6_electronics-13-01259-v2_FINAL_Rohner.pdf
- Kolar and Huber, Next-Generation SiC/GaN Three-Phase Variable-Speed Drive Inverter Concepts (2021), Fig. 1. https://www.pes-publications.ee.ethz.ch/uploads/tx_ethpublications/11_Kolar_and_Huber_-_2021_-_Next-generation_SiCGaN_three-phase_variable-speed.pdf

This is an original redraw informed by their presentation conventions; no published artwork or research data was copied.

## Conventions
- White background; black circuit lines; pale blue converter and pale green winding grouping.
- Blue #3070BE, red-orange #DA4D2A, green #378959; purple #7E379F for common-mode coupling.
- Serif labels, 8-pt native TikZ text; numerical plot labels 8.5 pt at approximately 88-mm width.
- Thin axes and light grids, solid/dashed trace distinctions, direct symbols, separate panels when quantities would crowd a dual-axis plot.
- Cell numbering runs from bottom cell 1 to top cell N in the electrical schematics, consistent with the common-mode reference definition.

## Editable sources and regeneration
- Shared vector theme: pes_figure_style.tex, included by main.tex.
- Architecture, switch stack and winding diagrams: fig_architecture.tex, fig_switch_stack.tex, fig_winding_options.tex.
- Common-mode circuit: ../Section-CommonMode/fig_spb_cm_equivalent.tex.
- Other native diagrams and plots remain in their corresponding Sections/*.tex files.
- MATLAB plots: ../Section-Intro/fig_intro_hv_motivation.m, ../Section-Intro/fig_intro_ronsp_trend.m, ../Section-DCLinkBalancing/fig_dclink_balancing.m, ../Section-Modulation/fig_dclink_ripple.m.
- Run rebuild_matlab_figures from MATLAB with this folder on the path. MATLAB scripts export editable FIG and vector PDF files.
- MATLAB could not run during this revision: network license checkout failed with error -96. The current PDF exports were generated using render_vector_plots.py (NumPy and Matplotlib required). MATLAB modifications remain unexecuted in this session; previously existing FIG files may therefore reflect the previous styling until the MATLAB rebuild succeeds.
- Python fallback: python Figures/Style/render_vector_plots.py from the project root (also works from other folders via its absolute source location).
- Rebuild the paper with pdfLaTeX, BibTeX if needed, and two pdfLaTeX passes.

## Content preservation
Original radar scores, semiconductor equations/constants and plotted domains are retained. The semiconductor figure uses a compact dual-axis graph: solid resistance curves on the left axis and dashed FOM curves on the right, with material indicated by color. Cell-count values are retained in a compact table beneath the plot.
Fig. 9 now uses analytical Fourier integrals of the ideal natural-SPWM input current over its switching intervals and the manuscript's shared dc-link transfer function. Crossing times use bisection; there is no ODE time stepping or startup transient. Both MATLAB `../Section-Modulation/fig_dclink_ripple.m` and Python `../Section-Modulation/fig_dclink_ripple_analytical.py` calculate this model independently. The CSV is regenerated, not used as input. The 8000-harmonic result is checked against 4000 harmonics and Parseval's RMS identity. Parameters and Python diagnostics are in `dclink_ripple_analytical_metrics.json`. Circuit values are normalized illustrative values, not hardware measurements. The original `../gen_fig_dclink_ripple.py` is a legacy time-domain example and does not generate the active manuscript figure. Fig. 12 uses an analytical small-signal illustration from the manuscript differential-mode equation: deviations grow under equal constant cell powers, then decay after proportional differential power feedback is enabled. Time is normalized; no physical simulation parameters or collapse trajectories are presented. Regenerate with `../Section-DCLinkBalancing/fig_dclink_balancing.m` or `fig_dclink_balancing_analytical.py`. The legacy nonlinear RK4 script is not used by the active manuscript figure.
Original external topology/winding assets are retained as legacy files, but the manuscript now includes the native vector replacements. No citations are removed.
