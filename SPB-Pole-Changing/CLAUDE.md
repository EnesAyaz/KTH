# SPB-Pole-Changing — agent team brief

## Research question
The Stacked Polyphase Bridge (SPB) splits a high-voltage traction inverter into N
series-stacked low-voltage modules so low-voltage GaN devices can be used. A side
effect: every module drives its own coil group with an **isolated neutral point**,
so the machine is inherently polyphase and the phase shift between coil groups is
set by modulation, not by wiring. **Can SPB do electronic pole changing (no
contactors) to extend the speed range and/or raise drive-cycle efficiency of
heavy-truck (and other traction/propulsion) drives?**

## Fixed facts (do not re-derive)
- SPB reference system: 1200 V DC link, 300 kW = 2 parallel 150 kW blocks per leg,
  N = 16 modules x 75 V class GaN (EPC2361). Loop inductance is 0.374 nH **per cell**.
- 75 V class choice comes from the gate-charge / L·di/dt loss model in
  `../Analytical Loss Calculations - GaN/LOSS_MODELING.md` — reuse it, don't rebuild it.
- Reusable sibling work: `../Airgap Harmonics/` (MMF scripts), `../Drive Cycle/`
  (vehicle dynamics, gearbox, drive cycles), `../LossCalculation-SPB/`, `../Modulation/`.
- Physics caveat: a PM rotor fixes the pole count. Pole changing applies directly to
  induction machines (cage adapts); PMSM/WFSM variants must be argued explicitly.

## Team (leader = main session; specialists in `.claude/agents/`)
| Agent | Owns folder | Produces |
|---|---|---|
| leader | `board/` | tasks, decisions, acceptance checks |
| lit-scout | `01_literature/` | `refs.bib`, `papers/<key>.md`, `gap_matrix.md` |
| analyst | `02_analytics/` | Python models + `results/*.json` |
| simulator | `03_simulation/` | models + `results/*.json`, `validation.md` |
| figure-maker | `04_figures/` | `<name>.py` + `.svg/.pdf/.png` |
| writer | `05_reports/` | paper (IEEE), slides, weekly notes |

## Leader protocol (one round per request from Enes)
1. **Plan** — turn the request into tasks in `board/tasks.md`, one owner each, with a
   done check. Say the plan in two or three lines before starting agents.
2. **Delegate** — start specialists as background agents (`subagent_type` = agent name).
   Parallel only when they do not write the same files: lit-scout + analyst are safe;
   analyst -> simulator -> figure-maker -> writer is ordered by data.
3. **Check** — verify each report against its done check; a failed check goes back to
   the same agent (SendMessage), not a new one.
4. **Close** — update the board, commit (agents never commit; Enes pushes from GitHub
   Desktop), report to Enes: what changed, the numbers, open questions.

The live agent map (mod in `tools/spb-agent-map/`) lights each agent while it works
and draws a handoff whenever an agent reads another agent's folder; it mirrors its
state to `board/agent_status.json`.

## Handoff protocol (the blackboard)
1. Agents talk through files, never through prose claims. A result exists only when
   it is in the owner's folder.
2. Each agent writes **only** inside its own folder (plus appending to `board/log.md`).
3. Every task lives in `board/tasks.md` with: id, owner, inputs (paths), output
   (paths), acceptance check. Only the leader adds or closes tasks.
4. On finishing, an agent appends one line to `board/log.md`:
   `YYYY-MM-DD HH:MM | <agent> | <task id> | <output paths> | <one-line result>`.
5. Numbers flow analyst/simulator -> JSON -> figure-maker/writer. Figure-maker never
   computes physics; writer never states a number that is not in a results file or
   refs.bib entry.
6. If analyst and simulator disagree by >5 % on a shared quantity, the leader opens a
   `reconcile` task for both before anything is plotted.
7. Decisions that change scope go to `board/decisions.md` with the reason.

## Conventions
- Python 3, numpy/scipy/matplotlib; scripts runnable from the repo root.
- SI units in files; JSON keys carry units (`torque_Nm`, `speed_rpm`).
- Figures: IEEE single column 3.5 in / double 7.16 in, Times-like font, vector output.
- Citations: BibTeX keys `FirstAuthorYEARword`; every entry needs a DOI or URL that
  was actually checked.
- Generated files stay out of git (see `.gitignore`); source, results JSON and figures go in.
