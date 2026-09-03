# Targeted Literature Requirements

This report identifies scientific information currently missing from the verified review database.

- Comparison records: 1
- Papers with full-text verified evidence: 1

## 1. Numerical Data Requirements

| Field | Valid | Target | Need | Priority |
|---|---:|---:|---:|---|
| `rated_power_kw` | 0 | 5 | 5 | CRITICAL |
| `peak_power_kw` | 0 | 3 | 3 | CRITICAL |
| `dc_link_voltage_v` | 1 | 5 | 4 | HIGH |
| `cell_voltage_v` | 1 | 5 | 4 | HIGH |
| `number_of_cells` | 1 | 5 | 4 | HIGH |
| `number_of_phases` | 1 | 5 | 4 | HIGH |
| `semiconductor_voltage_rating_v` | 0 | 5 | 5 | CRITICAL |
| `semiconductor_current_rating_a` | 0 | 3 | 3 | CRITICAL |
| `switching_frequency_khz` | 1 | 5 | 4 | HIGH |
| `efficiency_percent` | 0 | 5 | 5 | CRITICAL |
| `power_density_kw_per_l` | 0 | 3 | 3 | CRITICAL |

## 2. Quantitative Comparison Requirements

### Device voltage rating vs number of cells

- X: `number_of_cells`
- Y: `semiconductor_voltage_rating_v`
- Current paired records: 0
- Target paired records: 5
- Additional records needed: 5
- Priority: **CRITICAL**
- Scientific purpose: Demonstrate semiconductor voltage scaling enabled by converter stacking.

### Device voltage rating vs DC-link voltage

- X: `dc_link_voltage_v`
- Y: `semiconductor_voltage_rating_v`
- Current paired records: 0
- Target paired records: 5
- Additional records needed: 5
- Priority: **CRITICAL**
- Scientific purpose: Compare system DC voltage with the voltage class of semiconductor devices.

### Switching frequency vs semiconductor voltage

- X: `semiconductor_voltage_rating_v`
- Y: `switching_frequency_khz`
- Current paired records: 0
- Target paired records: 5
- Additional records needed: 5
- Priority: **CRITICAL**
- Scientific purpose: Investigate whether lower-voltage devices are associated with higher reported switching frequencies.

### Efficiency vs switching frequency

- X: `switching_frequency_khz`
- Y: `efficiency_percent`
- Current paired records: 0
- Target paired records: 5
- Additional records needed: 5
- Priority: **CRITICAL**
- Scientific purpose: Compare reported efficiency with switching frequency while preserving the operating conditions reported by each source.

### Efficiency vs power density

- X: `power_density_kw_per_l`
- Y: `efficiency_percent`
- Current paired records: 0
- Target paired records: 5
- Additional records needed: 5
- Priority: **CRITICAL**
- Scientific purpose: Assess the reported efficiency and power-density tradeoff.

### Rated power vs DC-link voltage

- X: `dc_link_voltage_v`
- Y: `rated_power_kw`
- Current paired records: 0
- Target paired records: 5
- Additional records needed: 5
- Priority: **CRITICAL**
- Scientific purpose: Show the experimental scale of reported converter and motor-drive demonstrations.

## 3. Priority Review Topics

### CRITICAL — Stacked polyphase bridge architecture

Missing quantitative fields:

- `dc_link_voltage_v`
- `cell_voltage_v`
- `number_of_cells`
- `number_of_phases`

Useful information to collect:

- DC-side series stacking arrangement
- number of bridge cells
- machine phase or winding-group arrangement
- cell voltage
- total DC-link voltage
- experimental validation

### CRITICAL — Semiconductor voltage scaling

Missing quantitative fields:

- `semiconductor_voltage_rating_v`
- `number_of_cells`
- `dc_link_voltage_v`
- `switching_frequency_khz`

Useful information to collect:

- semiconductor technology
- device voltage rating
- DC-link voltage
- number of stacked cells
- switching frequency
- device-count implications

### CRITICAL — Efficiency and loss comparison

Missing quantitative fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `switching_frequency_khz`
- `efficiency_percent`

Useful information to collect:

- measured efficiency
- output power
- DC-link voltage
- switching frequency
- semiconductor technology
- loss breakdown
- operating conditions

### CRITICAL — Power density and thermal management

Missing quantitative fields:

- `rated_power_kw`
- `power_density_kw_per_l`
- `efficiency_percent`

Useful information to collect:

- power density
- converter volume
- rated power
- cooling method
- thermal design
- measured efficiency

### CRITICAL — Integrated modular motor drives

Missing quantitative fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `number_of_phases`
- `efficiency_percent`
- `power_density_kw_per_l`

Useful information to collect:

- integrated inverter-machine architecture
- rated power
- DC-link voltage
- machine phase count
- cooling
- power density
- experimental maturity

### CRITICAL — Experimental demonstrations

Missing quantitative fields:

- `rated_power_kw`
- `dc_link_voltage_v`
- `switching_frequency_khz`
- `efficiency_percent`

Useful information to collect:

- hardware prototype
- rated power
- DC-link voltage
- switching frequency
- machine type
- experimental operating point
- efficiency

## 4. Recommended Literature Searches

### Search 1: Stacked polyphase bridge architecture

Priority: **CRITICAL**

Find peer-reviewed papers with experimental or quantitative results concerning Stacked polyphase bridge architecture. Prioritize publications reporting: DC-side series stacking arrangement, number of bridge cells, machine phase or winding-group arrangement, cell voltage, total DC-link voltage, experimental validation.

### Search 2: Semiconductor voltage scaling

Priority: **CRITICAL**

Find peer-reviewed papers with experimental or quantitative results concerning Semiconductor voltage scaling. Prioritize publications reporting: semiconductor technology, device voltage rating, DC-link voltage, number of stacked cells, switching frequency, device-count implications.

### Search 3: Efficiency and loss comparison

Priority: **CRITICAL**

Find peer-reviewed papers with experimental or quantitative results concerning Efficiency and loss comparison. Prioritize publications reporting: measured efficiency, output power, DC-link voltage, switching frequency, semiconductor technology, loss breakdown, operating conditions.

### Search 4: Power density and thermal management

Priority: **CRITICAL**

Find peer-reviewed papers with experimental or quantitative results concerning Power density and thermal management. Prioritize publications reporting: power density, converter volume, rated power, cooling method, thermal design, measured efficiency.

### Search 5: Integrated modular motor drives

Priority: **CRITICAL**

Find peer-reviewed papers with experimental or quantitative results concerning Integrated modular motor drives. Prioritize publications reporting: integrated inverter-machine architecture, rated power, DC-link voltage, machine phase count, cooling, power density, experimental maturity.

### Search 6: Experimental demonstrations

Priority: **CRITICAL**

Find peer-reviewed papers with experimental or quantitative results concerning Experimental demonstrations. Prioritize publications reporting: hardware prototype, rated power, DC-link voltage, switching frequency, machine type, experimental operating point, efficiency.
