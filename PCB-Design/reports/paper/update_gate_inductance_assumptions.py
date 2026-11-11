from pathlib import Path
from docx import Document
from docx.shared import Pt
import re

root = Path(__file__).parent
source = root / 'SPB_ICPE_complete_manuscript_with_Q3D_2026-10-29.docx'
output = root / 'SPB_ICPE_full_paper_revised_gate_loop_2026-11-02.docx'
doc = Document(source)
p = doc.paragraphs

def replace(i, value):
    q = p[i]
    fmt = q.runs[0]._r.rPr if q.runs else None
    from copy import deepcopy
    q.clear()
    run = q.add_run(value)
    if fmt is not None:
        run._r.insert(0, deepcopy(fmt))

replace(2, p[2].text.replace('Single-cell simulations and an electrical and thermal comparison support four parallel transistors per switch position for a candidate arrangement of sixteen submodules.', 'An initial single-cell and electrothermal study identifies four parallel transistors per switch position as a candidate for sixteen submodules. The revised design procedure adopts a 10 nH preliminary gate-loop case and a 20 nH sensitivity case; the earlier 1.7 nH results remain a reference pending recalculation.'))
replace(9, p[9].text.replace('Single-cell switching simulations establish a usable current range per device, and a comparison of losses, junction temperature, and voltage stress supports the selection of the parallel-device count.', 'Single-cell switching simulations and a comparison of losses, junction temperature, and voltage stress provide an initial parallel-count candidate. The revised sizing procedure assesses 10 nH and 20 nH gate-loop cases before accepting that candidate.'))
replace(35, 'The selected EPC2361 is evaluated in a half-bridge model with one device per switch position at a submodule voltage of 75 V. The revised preliminary study uses a gate-loop inductance of 10 nH as its nominal lumped case and 20 nH as a sensitivity case, together with commutation-loop inductances of 0.5 nH and 1 nH. The gate-loop quantity refers to the complete outgoing gate and return path between the driver and transistor; the commutation-loop inductance is treated separately. These gate-loop assumptions reflect the scale of the extracted DPT network more closely than the earlier 1.7 nH assumption. An external turn-on resistance of 2 Ω and a low-impedance turn-off path provide starting drive settings, which must be reassessed over both gate-loop cases. The saved numerical results in Figs. 3 and 4 and Table II were generated with 1.7 nH and have not yet been recalculated for 10 nH or 20 nH.')
replace(36, p[36].text.replace('Fig. 3 shows the simulated', 'Fig. 3 retains the earlier 1.7 nH gate-loop reference results for').replace('The higher-inductance case', 'The higher commutation-inductance case'))
replace(37, 'The earlier 1.7 nH results identify approximately 80 A as an initial current scale, suggesting four parallel transistors for the required 322 A phase-current peak. This establishes a layout candidate rather than a current limit validated with realistic gate routing. The revised study must repeat the current sweep for both 10 nH and 20 nH gate-loop cases, assess drain-voltage stress and gate excursions, and update the switching energies used in the parallel-count comparison. Four devices are retained provisionally until those cases and the extracted paired network confirm the electrical and thermal margins.')
replace(39, p[39].text + ' These are retained reference results with a 1.7 nH gate-loop model; the revised 10 nH and 20 nH sweeps are pending.')
replace(43, p[43].text + ' In the revised calculation, the switching-energy maps must be regenerated for the 10 nH and 20 nH gate-loop cases before the loss and thermal comparison is updated. The existing values remain conditional on the earlier 1.7 nH model.')
replace(45, p[45].text.replace('Fig. 4(a) shows', 'Fig. 4(a) retains the earlier 1.7 nH gate-loop calculation of') + ' These numerical loss reductions must be reassessed using the revised gate-loop cases.')
replace(47, p[47].text.replace('Preliminary parallel-count comparison', 'Earlier 1.7 nH gate-loop parallel-count comparison').replace('Four devices are the smallest tested count satisfying', 'Under that gate model, four devices are the smallest tested count satisfying') + ' Updated results for 10 nH and 20 nH are pending.')
replace(49, 'Table II retains the earlier comparison obtained with the 1.7 nH gate-loop model. Two devices exceed both the thermal and voltage limits in that calculation; three satisfy the thermal constraint but exceed the compact-loop voltage target. Four are the smallest tested count meeting both preliminary constraints under those assumptions. This result motivates a four-device layout candidate but does not establish compliance with the revised 10 nH and 20 nH gate-loop cases.')
replace(51, 'All numerical results in Table II retain the earlier 1.7 nH gate-loop assumption. Loss and junction-temperature estimates use the 0.5 nH commutation-loop case and the stated cooling model. Recalculation with 10 nH and 20 nH gate loops is required before accepting the parallel count.')
replace(52, 'Four devices are retained as a provisional implementation candidate and arranged as two identical transistor pairs. The earlier loss calculation does not identify an absolute minimum-loss solution: additional devices reduce the calculated losses but increase device count, gate loading, and routing complexity. The revised comparison must evaluate this tradeoff with 10 nH and 20 nH gate-loop models and then with the extracted paired network.')
replace(53, p[53].text.replace('Fig. 4(b) also shows', 'For the earlier 1.7 nH gate-loop case, Fig. 4(b) shows') + ' The effect of changing gate-loop inductance cannot be inferred by rescaling these voltage or energy values; it requires switching simulation with the corresponding drive network.')
replace(56, p[56].text + ' The 2 nH versus 8 nH perturbation is retained as an earlier mismatch example, not as the absolute gate-loop range adopted for preliminary sizing. Current sharing must also be checked around the revised 10 nH and 20 nH cases, separating common path inductance from branch mismatch.')
replace(62, p[62].text.replace('In the preliminary gate-drive comparison,', 'In the earlier gate-drive comparison,') + ' The quoted loading and energy differences must be reassessed with the revised gate-loop cases and the paired network.')
replace(69, 'The paired configuration is translated into a routed board and evaluated through the extraction-based workflow in Section V. Preliminary sizing now uses 10 nH and 20 nH gate-loop cases; extraction then replaces these lumped estimates with the actual shared and individual branches. The assessment determines whether the provisional current capability, parallel count, and switching margin can be retained.')
replace(72, 'The revised design sequence begins with assumed commutation-loop inductances of 0.5 nH and 1 nH and gate-loop cases of 10 nH and 20 nH. These assumptions are used to screen current range, drive settings, and parallel count before routing. Fig. 6 shows the iterative KiCad–Ansys Q3D–LTspice workflow that subsequently replaces the lumped assumptions with extracted networks. The saved 1.7 nH simulation results document the earlier sizing iteration and are not results of the revised screening.')
replace(79, 'The extracted DPT gate loops are 12.5 nH and 7.6 nH for the individual high-side and low-side paths, respectively, and 20.6 nH and 12.3 nH for the corresponding pair-driven paths in Fig. 7(d). These values motivate preliminary cases of 10 nH and 20 nH instead of 1.7 nH. The 20 nH case is a sensitivity point, not a guaranteed upper bound: the extracted high-side paired path is slightly higher. A single lumped value cannot reproduce all shared-path and mutual-coupling effects, so the final check uses the extracted network. Symmetry reduces mismatch but does not eliminate shared inductance.')
replace(86, p[86].text.replace('Table III compares the saved configurations.', 'Table III compares the saved configurations from the earlier design iteration; its preliminary-model cases use 1.7 nH. It does not contain results for the revised 10 nH and 20 nH cases.'))
replace(88, p[88].text.replace('retain the preliminary gate model', 'retain the earlier 1.7 nH gate model') + ' The 10 nH and 20 nH screening cases and the operating-board extracted gate model remain to be evaluated.')
replace(92, p[92].text.replace('retain the preliminary gate model', 'retain the earlier 1.7 nH gate model') + ' No waveform in this figure represents the revised 10 nH or 20 nH lumped case.')
replace(96, 'The design loop must first regenerate single-cell switching-energy and voltage-stress maps for 10 nH and 20 nH gate loops and use them to update the parallel-count, loss, and thermal comparison. The operating-board simulations must then use their corresponding extracted gate network before switching margin can be established. The paired DPT network provides a separate check of the measurement board. This feedback connects the physical building block to the initial SPB voltage choice: the expected benefit of low-voltage devices depends on the power and gate networks together.')
replace(106, 'A hardware-constrained procedure has been presented for a phase-leg building block of an SPB traction inverter. Charge-based device screening selects the 100 V EPC2361 from the surveyed candidates. The earlier 1.7 nH study provides a provisional four-device arrangement; the revised procedure adopts 10 nH and 20 nH gate-loop cases and requires updated electrical and thermal results before that count is accepted. Current-sharing sensitivity motivates paired gate drive, matched gate branches, and dedicated Kelvin returns.')

# Explicit model labels prevent the retained numerical table from appearing recalculated.
for row in doc.tables[2].rows[1:]:
    if row.cells[1].text == 'Preliminary':
        row.cells[1].text = 'Earlier 1.7 nH'

# Preserve the citation balance already established for this manuscript family.
refs = Document(root / 'SPB_ICPE_digest_expanded_citation_checked_2026-10-29.docx')
entries = [q.text for q in refs.paragraphs if re.match(r'^\[\d+\]',q.text)]
mapping = {1:1,3:2,4:3,5:4,6:5,7:6,8:7,9:8,10:9,11:10}
for q in doc.paragraphs[:109]:
    for run in q.runs:
        old=run.text
        val=old.replace('[2], [3]', '[3]')
        val=re.sub(r'\[(\d+)\]',lambda m:'['+str(mapping.get(int(m[1]),int(m[1])))+']',val)
        if val!=old:run.text=val
for q,val in zip(p[109:119],entries):
    q.clear();q.add_run(val)
p[119]._element.getparent().remove(p[119]._element)
qa=root/'icpe/gate_loop_revision_qa';qa.mkdir(exist_ok=True)
(qa/'artifact.md').write_text('Narrow full-manuscript edit preserving all headings, drawings, native equations, and source layout. Revised preliminary gate assumptions: 10 nH nominal and 20 nH sensitivity. Existing 1.7 nH numerical plots and tables explicitly identified as earlier results, not recalculated. Extracted DPT gate network preserved. Prior manuscript preserved. Self-citation balance retained at 2/10 references, or 2/8 scholarly works. Word PDF export and Poppler used for QA because bundled LibreOffice is unavailable.',encoding='utf-8')
doc.save(output)
print(output)
