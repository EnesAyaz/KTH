# VECTO declaration data (EU heavy-duty vehicle CO2 tool)

Source: official repository https://code.europa.eu/vecto/vecto, branch `stable`,
commit 68a719e7056b525fc715bac1987d2abc98a84148, path
`VectoCore/VectoCore/Resources/Declaration/` (downloaded 2026-10-29). VECTO is licensed EUPL-1.2.
Only data files were taken; no VECTO executable is downloaded or run.

| File | What |
|---|---|
| `LongHaul.vdri` | Long-haul mission cycle (D04 primary): 100.2 km, target speed up to 85 km/h (mean 83.4), grade -5.9 to +5.7 %, 67 s total stop time |
| `RegionalDelivery.vdri` | Regional delivery cycle (D04 secondary): 100 km, mean target 66.2 km/h, grade -8.5 to +6.2 % |
| `UrbanDelivery.vdri` | Urban delivery cycle (sensitivity): 100 km, mean target 47.7 km/h, grade -10.9 to +11.5 % |
| `SegmentTable.csv`, `Payloads.csv`, `Body_Trailers_Weights.csv` | Vehicle groups, payloads, body/trailer masses (group 5: 4x2 tractor + semitrailer, 40 t class) |

Cycle format: distance-based. `<s>` distance (m), `<v>` target speed (km/h), `<grad>` road gradient (%),
`<stop>` stop time at that point (s), `HW` highway flag. VECTO's driver model (acceleration limits,
look-ahead coasting) turns target speed into an actual speed trace; we need our own simple driver model.
