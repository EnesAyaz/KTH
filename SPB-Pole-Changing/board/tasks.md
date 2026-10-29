# Task board (leader edits; agents only read)

Status: todo | doing | done | blocked

| id | owner | status | inputs | output | acceptance check |
|---|---|---|---|---|---|
| T01 | leader | done | user brief | board/decisions.md: D01, D02 | D01 set by Enes; D02 provisional |
| T02 | lit-scout | done | CLAUDE.md | 01_literature/refs.bib, papers/*.md, gap_matrix.md | >=25 checked refs over 3 themes; gap matrix names >=3 gaps SPB fills |
| T02b | lit-scout | done | board/prior_work.md, Scholar | own-work + Bianchi + Peretti entries, revised gap_matrix.md | Enes papers tagged own-work; WRSM gap restated beyond P1-P3 |
| T03 | analyst | done | D01, D02 | 02_analytics/results/torque_speed_envelope.json | IM, PMSM, WRSM envelopes, each pole count; crossover speed; same SPB V/I limits for all |
| T04 | simulator | doing | T03 output | 03_simulation/results/*.json, validation.md | agrees with T03 within 5 % at 3 operating points |
| T03b | analyst | doing | T03 results, review notes | 02_analytics/results/fair_baselines.json | fixed-pole IM baselines designed for their own pole count; T03 file left untouched |
| T05 | figure-maker | todo | T03, T04 results | 04_figures/torque_speed_envelope.* | reads only results JSON |
| T06 | writer | todo | T02-T05 | 05_reports/weekly/2026-W44.md | every number traceable to a file |
