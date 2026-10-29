# Task board (leader edits; agents only read)

Status: todo | doing | done | blocked

| id | owner | status | inputs | output | acceptance check |
|---|---|---|---|---|---|
| T01 | leader | todo | user brief | board/decisions.md: machine type, vehicle spec | Enes agrees to D01/D02 |
| T02 | lit-scout | todo | CLAUDE.md | 01_literature/refs.bib, papers/*.md, gap_matrix.md | >=25 checked refs over 3 themes; gap matrix names >=3 gaps SPB fills |
| T03 | analyst | todo | D01, D02 | 02_analytics/results/torque_speed_envelope.json | envelope for each pole count; crossover speed stated |
| T04 | simulator | todo | T03 output | 03_simulation/results/*.json, validation.md | agrees with T03 within 5 % at 3 operating points |
| T05 | figure-maker | todo | T03, T04 results | 04_figures/torque_speed_envelope.* | reads only results JSON |
| T06 | writer | todo | T02-T05 | 05_reports/weekly/2026-W44.md | every number traceable to a file |
