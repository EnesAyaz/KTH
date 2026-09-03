# Quantitative Candidate Triage

This ranking estimates how useful each candidate may be for filling the current quantitative gaps.

**Important:** the score is not a measure of scientific quality and does not verify any technical value. All candidates remain `CANDIDATE_METADATA_ONLY` until their PDFs are processed by the full-text Evidence Extractor.

## Ranking

| Rank | Score | Recommendation | Category | Useful Fields | Pair Matches | Paper |
|---:|---:|---|---|---:|---:|---|
| 1 | 145 | DOWNLOAD FIRST | MODULAR_HIGH_VOLTAGE | 6 | 5 | Extreme high power density T-modular-multilevel-converter for medium voltage motor drive |
| 2 | 145 | DOWNLOAD FIRST | MODULAR_HIGH_VOLTAGE | 6 | 5 | High density Modular Multilevel Cascade Converter for medium-voltage motor drive |
| 3 | 142 | DOWNLOAD FIRST | MULTIPHASE_TRACTION | 6 | 4 | Design and Verification of Multiphase Multilevel Traction Inverter |
| 4 | 138 | DOWNLOAD FIRST | SIC_INTEGRATED_DRIVE | 6 | 4 | Control Strategy of a Hybrid SiC-Si Traction Inverter for Direct-Drive Multiphase PMSMs in Marine Propulsion |
| 5 | 138 | DOWNLOAD FIRST | SIC_INTEGRATED_DRIVE | 6 | 4 | High efficiency SiC traction inverter for electric vehicle applications |
| 6 | 137 | DOWNLOAD / RESERVE | GAN_INTEGRATED_DRIVE | 6 | 4 | Design and Analysis of a GaN-Based Megahertz Integrated Motor Drive for a PCB Motor |
| 7 | 133 | DOWNLOAD / RESERVE | GAN_INTEGRATED_DRIVE | 6 | 4 | GaN based High Power Density PCB Design for Aerial Vehicles Motor Drive Applications |
| 8 | 132 | DOWNLOAD / RESERVE | GAN_INTEGRATED_DRIVE | 6 | 4 | Comparison of Inverter Topologies Suited for Integrated Modular Motor Drive Applications |
| 9 | 115 | HOLD | SIC_INTEGRATED_DRIVE | 6 | 3 | 1500 V and 10 A SiC motor drive inverter module |
| 10 | 88 | HOLD | SIC_INTEGRATED_DRIVE | 4 | 2 | Design and Research on High Power Density Motor of Integrated Motor Drive System for Electric Vehicles |

## Candidate Details

### 1. Extreme high power density T-modular-multilevel-converter for medium voltage motor drive

- Score: **145**
- Recommendation: **DOWNLOAD FIRST**
- Architecture category: `MODULAR_HIGH_VOLTAGE`
- DOI: 10.1109/iecon.2017.8216194
- Year: 2017
- Experimental relevance: MEDIUM
- Quantitative relevance: HIGH
- Full-text access likelihood: MEDIUM
- Useful missing fields: 6

Expected useful fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `cell_voltage_v`
- `number_of_cells`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`
- `cooling_method`

Matched figure pairs:

- Efficiency vs power density
- Semiconductor voltage rating vs switching frequency
- Efficiency vs switching frequency
- Cell voltage vs semiconductor voltage rating
- Rated power vs DC-link voltage

Score components:

- FIELD: dc_link_voltage_v (+5)
- FIELD: efficiency_percent (+10)
- FIELD: power_density_kw_per_l (+11)
- FIELD: rated_power_kw (+6)
- FIELD: semiconductor_voltage_rating_v (+9)
- FIELD: switching_frequency_khz (+8)
- PAIR: Efficiency vs power density (+16)
- PAIR: Semiconductor voltage rating vs switching frequency (+14)
- PAIR: Efficiency vs switching frequency (+14)
- PAIR: Cell voltage vs semiconductor voltage rating (+12)
- PAIR: Rated power vs DC-link voltage (+10)
- EXPERIMENTAL: MEDIUM (+4)
- QUANTITATIVE: HIGH (+8)
- ACCESS: MEDIUM (+2)
- TOPIC: Q05 (+5)
- DOI: 10.1109/iecon.2017.8216194 (+3)
- MULTI_FIELD: 6 useful fields (+8)

Discovery-stage rationale:

Explicit high-power-density modular multilevel motor-drive architecture; likely useful as a benchmark for density and voltage-partitioned modular conversion.

### 2. High density Modular Multilevel Cascade Converter for medium-voltage motor drive

- Score: **145**
- Recommendation: **DOWNLOAD FIRST**
- Architecture category: `MODULAR_HIGH_VOLTAGE`
- DOI: 10.1109/ests.2011.5770920
- Year: 2011
- Experimental relevance: MEDIUM
- Quantitative relevance: HIGH
- Full-text access likelihood: MEDIUM
- Useful missing fields: 6

Expected useful fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `cell_voltage_v`
- `number_of_cells`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`
- `cooling_method`

Matched figure pairs:

- Efficiency vs power density
- Semiconductor voltage rating vs switching frequency
- Efficiency vs switching frequency
- Cell voltage vs semiconductor voltage rating
- Rated power vs DC-link voltage

Score components:

- FIELD: dc_link_voltage_v (+5)
- FIELD: efficiency_percent (+10)
- FIELD: power_density_kw_per_l (+11)
- FIELD: rated_power_kw (+6)
- FIELD: semiconductor_voltage_rating_v (+9)
- FIELD: switching_frequency_khz (+8)
- PAIR: Efficiency vs power density (+16)
- PAIR: Semiconductor voltage rating vs switching frequency (+14)
- PAIR: Efficiency vs switching frequency (+14)
- PAIR: Cell voltage vs semiconductor voltage rating (+12)
- PAIR: Rated power vs DC-link voltage (+10)
- EXPERIMENTAL: MEDIUM (+4)
- QUANTITATIVE: HIGH (+8)
- ACCESS: MEDIUM (+2)
- TOPIC: Q05 (+5)
- DOI: 10.1109/ests.2011.5770920 (+3)
- MULTI_FIELD: 6 useful fields (+8)

Discovery-stage rationale:

Directly concerns a high-density modular converter for medium-voltage motor drives and is relevant to lower-voltage-device voltage partitioning.

### 3. Design and Verification of Multiphase Multilevel Traction Inverter

- Score: **142**
- Recommendation: **DOWNLOAD FIRST**
- Architecture category: `MULTIPHASE_TRACTION`
- DOI: 10.3390/app142210562
- Year: 2024
- Experimental relevance: HIGH
- Quantitative relevance: HIGH
- Full-text access likelihood: HIGH
- Useful missing fields: 6

Expected useful fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `number_of_phases`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`

Matched figure pairs:

- Efficiency vs power density
- Semiconductor voltage rating vs switching frequency
- Efficiency vs switching frequency
- Rated power vs DC-link voltage

Score components:

- FIELD: dc_link_voltage_v (+5)
- FIELD: efficiency_percent (+10)
- FIELD: power_density_kw_per_l (+11)
- FIELD: rated_power_kw (+6)
- FIELD: semiconductor_voltage_rating_v (+9)
- FIELD: switching_frequency_khz (+8)
- PAIR: Efficiency vs power density (+16)
- PAIR: Semiconductor voltage rating vs switching frequency (+14)
- PAIR: Efficiency vs switching frequency (+14)
- PAIR: Rated power vs DC-link voltage (+10)
- EXPERIMENTAL: HIGH (+8)
- QUANTITATIVE: HIGH (+8)
- ACCESS: HIGH (+4)
- TOPIC: Q04, Q05 (+8)
- DOI: 10.3390/app142210562 (+3)
- MULTI_FIELD: 6 useful fields (+8)

Discovery-stage rationale:

Title explicitly indicates design verification of a multiphase multilevel traction inverter, making it a promising prototype benchmark for electrical and performance fields.

### 4. Control Strategy of a Hybrid SiC-Si Traction Inverter for Direct-Drive Multiphase PMSMs in Marine Propulsion

- Score: **138**
- Recommendation: **DOWNLOAD FIRST**
- Architecture category: `SIC_INTEGRATED_DRIVE`
- DOI: 10.1109/tpel.2024.3434703
- Year: 2024
- Experimental relevance: HIGH
- Quantitative relevance: HIGH
- Full-text access likelihood: MEDIUM
- Useful missing fields: 6

Expected useful fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `number_of_phases`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`

Matched figure pairs:

- Efficiency vs power density
- Semiconductor voltage rating vs switching frequency
- Efficiency vs switching frequency
- Rated power vs DC-link voltage

Score components:

- FIELD: dc_link_voltage_v (+5)
- FIELD: efficiency_percent (+10)
- FIELD: power_density_kw_per_l (+11)
- FIELD: rated_power_kw (+6)
- FIELD: semiconductor_voltage_rating_v (+9)
- FIELD: switching_frequency_khz (+8)
- PAIR: Efficiency vs power density (+16)
- PAIR: Semiconductor voltage rating vs switching frequency (+14)
- PAIR: Efficiency vs switching frequency (+14)
- PAIR: Rated power vs DC-link voltage (+10)
- EXPERIMENTAL: HIGH (+8)
- QUANTITATIVE: HIGH (+8)
- ACCESS: MEDIUM (+2)
- TOPIC: Q03, Q04 (+6)
- DOI: 10.1109/tpel.2024.3434703 (+3)
- MULTI_FIELD: 6 useful fields (+8)

Discovery-stage rationale:

Multiphase traction-scale marine propulsion application with hybrid SiC–Si devices; strong candidate for phase count, electrical ratings, switching, and efficiency data.

### 5. High efficiency SiC traction inverter for electric vehicle applications

- Score: **138**
- Recommendation: **DOWNLOAD FIRST**
- Architecture category: `SIC_INTEGRATED_DRIVE`
- DOI: 10.1109/apec.2018.8341204
- Year: 2018
- Experimental relevance: HIGH
- Quantitative relevance: HIGH
- Full-text access likelihood: MEDIUM
- Useful missing fields: 6

Expected useful fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`
- `cooling_method`

Matched figure pairs:

- Efficiency vs power density
- Semiconductor voltage rating vs switching frequency
- Efficiency vs switching frequency
- Rated power vs DC-link voltage

Score components:

- FIELD: dc_link_voltage_v (+5)
- FIELD: efficiency_percent (+10)
- FIELD: power_density_kw_per_l (+11)
- FIELD: rated_power_kw (+6)
- FIELD: semiconductor_voltage_rating_v (+9)
- FIELD: switching_frequency_khz (+8)
- PAIR: Efficiency vs power density (+16)
- PAIR: Semiconductor voltage rating vs switching frequency (+14)
- PAIR: Efficiency vs switching frequency (+14)
- PAIR: Rated power vs DC-link voltage (+10)
- EXPERIMENTAL: HIGH (+8)
- QUANTITATIVE: HIGH (+8)
- ACCESS: MEDIUM (+2)
- TOPIC: Q03, Q04 (+6)
- DOI: 10.1109/apec.2018.8341204 (+3)
- MULTI_FIELD: 6 useful fields (+8)

Discovery-stage rationale:

Traction-focused SiC inverter paper explicitly emphasizing efficiency; promising source for device, switching, power, voltage, and possibly density data.

### 6. Design and Analysis of a GaN-Based Megahertz Integrated Motor Drive for a PCB Motor

- Score: **137**
- Recommendation: **DOWNLOAD / RESERVE**
- Architecture category: `GAN_INTEGRATED_DRIVE`
- DOI: 10.1109/tie.2024.3390736
- Year: 2024
- Experimental relevance: HIGH
- Quantitative relevance: HIGH
- Full-text access likelihood: MEDIUM
- Useful missing fields: 6

Expected useful fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`
- `cooling_method`

Matched figure pairs:

- Efficiency vs power density
- Semiconductor voltage rating vs switching frequency
- Efficiency vs switching frequency
- Rated power vs DC-link voltage

Score components:

- FIELD: dc_link_voltage_v (+5)
- FIELD: efficiency_percent (+10)
- FIELD: power_density_kw_per_l (+11)
- FIELD: rated_power_kw (+6)
- FIELD: semiconductor_voltage_rating_v (+9)
- FIELD: switching_frequency_khz (+8)
- PAIR: Efficiency vs power density (+16)
- PAIR: Semiconductor voltage rating vs switching frequency (+14)
- PAIR: Efficiency vs switching frequency (+14)
- PAIR: Rated power vs DC-link voltage (+10)
- EXPERIMENTAL: HIGH (+8)
- QUANTITATIVE: HIGH (+8)
- ACCESS: MEDIUM (+2)
- TOPIC: Q02 (+5)
- DOI: 10.1109/tie.2024.3390736 (+3)
- MULTI_FIELD: 6 useful fields (+8)

Discovery-stage rationale:

Integrated GaN motor drive with an explicitly megahertz operating concept; likely to contain prototype operating data and compactness-related metrics.

### 7. GaN based High Power Density PCB Design for Aerial Vehicles Motor Drive Applications

- Score: **133**
- Recommendation: **DOWNLOAD / RESERVE**
- Architecture category: `GAN_INTEGRATED_DRIVE`
- DOI: 10.1109/iwipp61784.2025.10971516
- Year: 2025
- Experimental relevance: MEDIUM
- Quantitative relevance: HIGH
- Full-text access likelihood: MEDIUM
- Useful missing fields: 6

Expected useful fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`
- `cooling_method`

Matched figure pairs:

- Efficiency vs power density
- Semiconductor voltage rating vs switching frequency
- Efficiency vs switching frequency
- Rated power vs DC-link voltage

Score components:

- FIELD: dc_link_voltage_v (+5)
- FIELD: efficiency_percent (+10)
- FIELD: power_density_kw_per_l (+11)
- FIELD: rated_power_kw (+6)
- FIELD: semiconductor_voltage_rating_v (+9)
- FIELD: switching_frequency_khz (+8)
- PAIR: Efficiency vs power density (+16)
- PAIR: Semiconductor voltage rating vs switching frequency (+14)
- PAIR: Efficiency vs switching frequency (+14)
- PAIR: Rated power vs DC-link voltage (+10)
- EXPERIMENTAL: MEDIUM (+4)
- QUANTITATIVE: HIGH (+8)
- ACCESS: MEDIUM (+2)
- TOPIC: Q02 (+5)
- DOI: 10.1109/iwipp61784.2025.10971516 (+3)
- MULTI_FIELD: 6 useful fields (+8)

Discovery-stage rationale:

Explicitly targets high-power-density GaN motor-drive hardware for aerial vehicles; promising benchmark for density, switching, efficiency, and cooling metrics.

### 8. Comparison of Inverter Topologies Suited for Integrated Modular Motor Drive Applications

- Score: **132**
- Recommendation: **DOWNLOAD / RESERVE**
- Architecture category: `GAN_INTEGRATED_DRIVE`
- DOI: 10.1109/epepemc.2018.8521918
- Year: 2018
- Experimental relevance: MEDIUM
- Quantitative relevance: MEDIUM
- Full-text access likelihood: MEDIUM
- Useful missing fields: 6

Expected useful fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`
- `cooling_method`

Matched figure pairs:

- Efficiency vs power density
- Semiconductor voltage rating vs switching frequency
- Efficiency vs switching frequency
- Rated power vs DC-link voltage

Score components:

- FIELD: dc_link_voltage_v (+5)
- FIELD: efficiency_percent (+10)
- FIELD: power_density_kw_per_l (+11)
- FIELD: rated_power_kw (+6)
- FIELD: semiconductor_voltage_rating_v (+9)
- FIELD: switching_frequency_khz (+8)
- PAIR: Efficiency vs power density (+16)
- PAIR: Semiconductor voltage rating vs switching frequency (+14)
- PAIR: Efficiency vs switching frequency (+14)
- PAIR: Rated power vs DC-link voltage (+10)
- EXPERIMENTAL: MEDIUM (+4)
- QUANTITATIVE: MEDIUM (+4)
- ACCESS: MEDIUM (+2)
- TOPIC: Q02, Q03 (+8)
- DOI: 10.1109/epepemc.2018.8521918 (+3)
- MULTI_FIELD: 6 useful fields (+8)

Discovery-stage rationale:

Directly addresses integrated modular motor-drive inverter topology tradeoffs and may provide comparable efficiency, density, device, and switching data.

### 9. 1500 V and 10 A SiC motor drive inverter module

- Score: **115**
- Recommendation: **HOLD**
- Architecture category: `SIC_INTEGRATED_DRIVE`
- DOI: 10.1109/wct.2004.240150
- Year: 2004
- Experimental relevance: HIGH
- Quantitative relevance: HIGH
- Full-text access likelihood: MEDIUM
- Useful missing fields: 6

Expected useful fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `semiconductor_voltage_rating_v`
- `semiconductor_current_rating_a`
- `switching_frequency_khz`
- `efficiency_percent`
- `cooling_method`

Matched figure pairs:

- Semiconductor voltage rating vs switching frequency
- Efficiency vs switching frequency
- Rated power vs DC-link voltage

Score components:

- FIELD: dc_link_voltage_v (+5)
- FIELD: efficiency_percent (+10)
- FIELD: rated_power_kw (+6)
- FIELD: semiconductor_current_rating_a (+7)
- FIELD: semiconductor_voltage_rating_v (+9)
- FIELD: switching_frequency_khz (+8)
- PAIR: Semiconductor voltage rating vs switching frequency (+14)
- PAIR: Efficiency vs switching frequency (+14)
- PAIR: Rated power vs DC-link voltage (+10)
- EXPERIMENTAL: HIGH (+8)
- QUANTITATIVE: HIGH (+8)
- ACCESS: MEDIUM (+2)
- TOPIC: Q03 (+3)
- DOI: 10.1109/wct.2004.240150 (+3)
- MULTI_FIELD: 6 useful fields (+8)

Discovery-stage rationale:

Explicit SiC motor-drive inverter module with device-level voltage/current emphasis; especially valuable for the current semiconductor-rating gaps.

### 10. Design and Research on High Power Density Motor of Integrated Motor Drive System for Electric Vehicles

- Score: **88**
- Recommendation: **HOLD**
- Architecture category: `SIC_INTEGRATED_DRIVE`
- DOI: 10.3390/en15103542
- Year: 2022
- Experimental relevance: MEDIUM
- Quantitative relevance: HIGH
- Full-text access likelihood: HIGH
- Useful missing fields: 4

Expected useful fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `efficiency_percent`
- `power_density_kw_per_l`
- `cooling_method`

Matched figure pairs:

- Efficiency vs power density
- Rated power vs DC-link voltage

Score components:

- FIELD: dc_link_voltage_v (+5)
- FIELD: efficiency_percent (+10)
- FIELD: power_density_kw_per_l (+11)
- FIELD: rated_power_kw (+6)
- PAIR: Efficiency vs power density (+16)
- PAIR: Rated power vs DC-link voltage (+10)
- EXPERIMENTAL: MEDIUM (+4)
- QUANTITATIVE: HIGH (+8)
- ACCESS: HIGH (+4)
- TOPIC: Q03, Q04 (+6)
- DOI: 10.3390/en15103542 (+3)
- MULTI_FIELD: 4 useful fields (+5)

Discovery-stage rationale:

Explicit high-power-density integrated electric-drive study; likely useful for system-level density, power, efficiency, and thermal/cooling benchmarking.

## Current Field Weights

| Field | Weight | Additional Records Needed |
|---|---:|---:|
| `power_density_kw_per_l` | 11 | 5 |
| `efficiency_percent` | 10 | 4 |
| `semiconductor_voltage_rating_v` | 9 | 3 |
| `switching_frequency_khz` | 8 | 2 |
| `semiconductor_current_rating_a` | 7 | 5 |
| `rated_power_kw` | 6 | 2 |
| `dc_link_voltage_v` | 5 | 1 |
| `cell_voltage_v` | 0 | 0 |
| `number_of_cells` | 0 | 0 |
| `number_of_phases` | 0 | 0 |

## Current Pair Weights

| Relationship | Weight | Additional Pairs Needed |
|---|---:|---:|
| Efficiency vs power density | 16 | 5 |
| Efficiency vs switching frequency | 14 | 4 |
| Semiconductor voltage rating vs switching frequency | 14 | 4 |
| Cell voltage vs semiconductor voltage rating | 12 | 3 |
| Rated power vs DC-link voltage | 10 | 3 |

## Selection Note

The next step should select approximately 5-8 papers while maintaining architectural diversity. Do not automatically download every high-scoring paper if several candidates describe essentially the same system or research group.
