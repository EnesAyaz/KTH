# Quantitative Literature Targets

This report converts the current comparison database coverage into explicit targets for the next literature-search round.

Current comparison records: 6

## Individual Field Coverage

| Field | Available | Target | Additional Needed | Priority | Status |
|---|---:|---:|---:|---|---|
| `power_density_kw_per_l` | 0 | 5 | 5 | CRITICAL | NO DATA |
| `efficiency_percent` | 2 | 6 | 4 | CRITICAL | MORE DATA NEEDED |
| `semiconductor_voltage_rating_v` | 3 | 6 | 3 | CRITICAL | MORE DATA NEEDED |
| `switching_frequency_khz` | 4 | 6 | 2 | CRITICAL | MORE DATA NEEDED |
| `rated_power_kw` | 4 | 6 | 2 | HIGH | MORE DATA NEEDED |
| `dc_link_voltage_v` | 5 | 6 | 1 | HIGH | MORE DATA NEEDED |
| `cell_voltage_v` | 6 | 6 | 0 | HIGH | TARGET MET |
| `semiconductor_current_rating_a` | 0 | 5 | 5 | MEDIUM | NO DATA |
| `number_of_cells` | 6 | 6 | 0 | MEDIUM | TARGET MET |
| `number_of_phases` | 6 | 6 | 0 | MEDIUM | TARGET MET |

## Paired Quantitative Coverage

| Figure Relationship | Current Pairs | Target | Additional Needed | Priority |
|---|---:|---:|---:|---|
| Efficiency vs power density | 0 | 5 | 5 | CRITICAL |
| Semiconductor voltage rating vs switching frequency | 2 | 6 | 4 | CRITICAL |
| Efficiency vs switching frequency | 2 | 6 | 4 | CRITICAL |
| Cell voltage vs semiconductor voltage rating | 3 | 6 | 3 | CRITICAL |
| Rated power vs DC-link voltage | 3 | 6 | 3 | HIGH |

## Priority Literature Search Topics

### Q01 — Experimental stacked polyphase bridge converter implementations

Priority: **CRITICAL**

Desired fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `cell_voltage_v`
- `number_of_cells`
- `number_of_phases`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`
- `efficiency_percent`

Selection goal:

Find direct SPB publications containing actual prototype specifications and quantitative converter data.

### Q02 — GaN integrated modular motor drives with quantitative performance

Priority: **CRITICAL**

Desired fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`
- `cooling_method`

Selection goal:

Find experimentally validated GaN integrated-drive systems reporting both efficiency and power-density metrics.

### Q03 — SiC integrated motor drives with efficiency and power density

Priority: **HIGH**

Desired fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`
- `cooling_method`

Selection goal:

Provide a strong SiC benchmark against the GaN and stacked architectures.

### Q04 — Multiphase high-power traction inverter experimental demonstrations

Priority: **HIGH**

Desired fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `number_of_phases`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`

Selection goal:

Provide high-power traction-scale benchmarks with comparable voltage, power, semiconductor, switching, and efficiency data.

### Q05 — High-voltage modular motor-drive architectures using lower-voltage semiconductor devices

Priority: **CRITICAL**

Desired fields:

- `dc_link_voltage_v`
- `cell_voltage_v`
- `number_of_cells`
- `number_of_phases`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`

Selection goal:

Strengthen the central SPB review argument concerning DC-link voltage partitioning and semiconductor voltage scaling.

## Ideal Candidate

An ideal candidate reports at least four of the following in one experimentally demonstrated system: rated power, DC-link voltage, cell voltage, semiconductor voltage rating, switching frequency, efficiency, and power density.

## Important Semantic Warning

`number_of_cells` must not automatically combine SPB series cells, generic inverter modules, phase modules, and segmented drive units. These architectures must be classified before using the values in the same figure.

In particular, architecture counts from integrated modular motor-drive papers should not be interpreted as SPB series-cell counts unless the full text explicitly supports that interpretation.
