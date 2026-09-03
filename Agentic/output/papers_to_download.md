# Candidate Papers to Download

These publications were identified through targeted literature discovery.

**Important:** They are not yet full-text verified.
Download and place selected PDFs in the `papers/` folder before scientific claims are used.

## Search Summary

Targeted bibliographic search identified strong candidate publications addressing stacked polyphase bridge architectures, modular motor-drive experiments, semiconductor voltage scaling, efficiency/loss comparison, and power density/thermal management. Candidates are metadata-verified only; numerical fields must be checked in the full text. Existing project papers were excluded.

## Candidates (13)

### 1. Modulation and Power Losses of a Stacked Polyphase Bridge Converter

**Authors:** Lebing Jin, Staffan Norrga, Oskar Wallmark, Nikolaos Apostolopoulos

**Year:** 2017

**Venue:** IEEE Journal of Emerging and Selected Topics in Power Electronics

**DOI:** `10.1109/JESTPE.2016.2621349`

**URL:** https://doi.org/10.1109/JESTPE.2016.2621349

**Type:** Journal article

**Target topics:**

- Stacked polyphase bridge architecture
- Efficiency and loss comparison
- Semiconductor voltage scaling

**Potential comparison fields:**

- `number_of_cells`
- `number_of_phases`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`
- `efficiency_percent`

**Why this paper may be useful:**

Foundational SPB-converter paper explicitly focused on modulation and power losses; potentially useful for device-stress, cell-count, switching-frequency, and loss comparisons.

**Experimental relevance:**

Potentially includes converter implementation or validation; full-text inspection is required.

**Expected full-text value:**

High for architecture and loss-model fields; uncertain for rated power and power density.

**Current verification:** `CANDIDATE_METADATA_ONLY`

---

### 2. Comparison of optimized motor-inverter systems using a Stacked Polyphase Bridge Converter combined with a 3-, 6-, 9-, or 12-phase PMSM

**Authors:** Thilo Bringezu, Jürgen Biela

**Year:** 2020

**Venue:** 2020 22nd European Conference on Power Electronics and Applications (EPE'20 ECCE Europe)

**DOI:** `10.23919/EPE20ECCEEurope43536.2020.9215873`

**URL:** https://doi.org/10.23919/EPE20ECCEEurope43536.2020.9215873

**Type:** Conference paper

**Target topics:**

- Stacked polyphase bridge architecture
- Integrated modular motor drives
- Experimental demonstrations

**Potential comparison fields:**

- `rated_power_kw`
- `dc_link_voltage_v`
- `cell_voltage_v`
- `number_of_cells`
- `number_of_phases`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`

**Why this paper may be useful:**

Directly compares SPB converters combined with 3-, 6-, 9-, and 12-phase PMSMs, making it highly valuable for phase-count, module-count, voltage-scaling, and system-level comparison.

**Experimental relevance:**

Appears primarily comparative/design-oriented; experimental scope and measured quantities require PDF verification.

**Expected full-text value:**

Very high for cross-topology architecture and quantitative system comparison.

**Current verification:** `CANDIDATE_METADATA_ONLY`

---

### 3. Control of a 9-Phase PMSM with Stacked Polyphase Bridge Converter including DC Source Impedance

**Authors:** Thilo Bringezu, Jürgen Biela

**Year:** 2023

**Venue:** 2023 25th European Conference on Power Electronics and Applications (EPE'23 ECCE Europe)

**DOI:** `10.23919/EPE23ECCEEurope58414.2023.10264521`

**URL:** https://doi.org/10.23919/EPE23ECCEEurope58414.2023.10264521

**Type:** Conference paper

**Target topics:**

- Stacked polyphase bridge architecture
- Experimental demonstrations

**Potential comparison fields:**

- `dc_link_voltage_v`
- `cell_voltage_v`
- `number_of_cells`
- `number_of_phases`
- `switching_frequency_khz`
- `rated_power_kw`

**Why this paper may be useful:**

Focused 9-phase SPB motor-drive study potentially providing a concrete multi-cell, multi-winding operating point and converter-control validation.

**Experimental relevance:**

Likely includes simulation and/or experimental 9-phase PMSM results; full text is needed to confirm.

**Expected full-text value:**

High for 9-phase architecture and operating-point data; efficiency may be absent.

**Current verification:** `CANDIDATE_METADATA_ONLY`

---

### 4. Communication-Based Distributed Control of the Stacked Polyphase Bridges Converter

**Authors:** Lebing Jin, Staffan Norrga, Oskar Wallmark, Nikolaos Apostolopoulos

**Year:** 2018

**Venue:** IEEE Transactions on Industrial Electronics

**DOI:** `10.1109/TIE.2017.2723874`

**URL:** https://doi.org/10.1109/TIE.2017.2723874

**Type:** Journal article

**Target topics:**

- Stacked polyphase bridge architecture
- Experimental demonstrations

**Potential comparison fields:**

- `number_of_cells`
- `number_of_phases`
- `dc_link_voltage_v`
- `cell_voltage_v`
- `switching_frequency_khz`
- `rated_power_kw`

**Why this paper may be useful:**

Important SPB control paper addressing scalable distributed control of multiple series-connected converter submodules; potentially useful for practical cell-count and voltage-distribution data.

**Experimental relevance:**

Likely includes a laboratory converter demonstration.

**Expected full-text value:**

High for architecture implementation and distributed-control validation; uncertain for efficiency and power density.

**Current verification:** `CANDIDATE_METADATA_ONLY`

---

### 5. Dynamic multi-agent dc-bus reconfiguration in modular motor drives with a stacked polyphase bridge converter

**Authors:** Lynn Verkroost, Alexander Vande Ghinste, Lorrana Faria da Rocha, Jeroen D. M. De Kooning, Frederik De Belie, Peter Sergeant, Pål Keim Olsen, Hendrik Vansompel

**Year:** 2024

**Venue:** IET Electric Power Applications

**DOI:** `10.1049/elp2.12376`

**URL:** https://doi.org/10.1049/elp2.12376

**Type:** Journal article

**Target topics:**

- Stacked polyphase bridge architecture
- Integrated modular motor drives
- Experimental demonstrations

**Potential comparison fields:**

- `rated_power_kw`
- `dc_link_voltage_v`
- `cell_voltage_v`
- `number_of_cells`
- `number_of_phases`
- `switching_frequency_khz`

**Why this paper may be useful:**

Peer-reviewed experimental study of a 4 kW modular axial-flux PMSM with five SPB agents; likely useful for phase/winding-group count, series-cell structure, voltage allocation, and hardware maturity.

**Experimental relevance:**

Strong: reported experimental validation on a 4 kW multi-three-phase axial-flux PMSM.

**Expected full-text value:**

Very high for architecture and experimental-scale fields; efficiency and semiconductor ratings must be extracted from the PDF.

**Current verification:** `CANDIDATE_METADATA_ONLY`

---

### 6. Multi-Agent Control Scheme for Power Distribution in a Multi-Three-Phase Motor Drive Fed by a Stacked Polyphase Bridges Converter

**Authors:** Lynn Verkroost, Frederik De Belie, Lorrana Faria da Rocha, Pål Keim Olsen, Peter Sergeant, Hendrik Vansompel

**Year:** 2024

**Venue:** IEEE Transactions on Energy Conversion

**DOI:** `10.1109/TEC.2024.3405368`

**URL:** https://doi.org/10.1109/TEC.2024.3405368

**Type:** Journal article

**Target topics:**

- Stacked polyphase bridge architecture
- Integrated modular motor drives
- Experimental demonstrations

**Potential comparison fields:**

- `rated_power_kw`
- `dc_link_voltage_v`
- `cell_voltage_v`
- `number_of_cells`
- `number_of_phases`
- `efficiency_percent`

**Why this paper may be useful:**

Directly studies power sharing in a multi-three-phase SPB-fed motor drive and is likely to contain laboratory operating data complementary to the reconfiguration paper.

**Experimental relevance:**

Likely includes experimental validation of a modular motor-drive platform.

**Expected full-text value:**

High for multi-agent architecture, power distribution, and drive-scale comparison.

**Current verification:** `CANDIDATE_METADATA_ONLY`

---

### 7. An Integrated Motor Drive with Enhanced Power Density Using Modular Converter Structure

**Authors:** Authors require confirmation from the full bibliographic record

**Year:** 2021

**Venue:** 2021 IEEE International Electric Machines & Drives Conference (IEMDC)

**DOI:** `10.1109/IEMDC47953.2021.9449589`

**URL:** https://doi.org/10.1109/IEMDC47953.2021.9449589

**Type:** Conference paper

**Target topics:**

- Integrated modular motor drives
- Power density and thermal management
- Experimental demonstrations

**Potential comparison fields:**

- `rated_power_kw`
- `number_of_cells`
- `number_of_phases`
- `semiconductor_voltage_rating_v`
- `efficiency_percent`
- `power_density_kw_per_l`

**Why this paper may be useful:**

Experimental modular GaN inverter structure integrated with a fifteen-coil axial-flux PM machine; potentially valuable for converter-module count, thermal limits, cooling-channel design, and power-density comparison.

**Experimental relevance:**

Strong: CFD cooling analysis was reportedly validated by experimental measurements.

**Expected full-text value:**

Very high for integrated packaging and thermal-management fields; DC-link and efficiency data require verification.

**Current verification:** `CANDIDATE_METADATA_ONLY`

---

### 8. Comparative Evaluation of Three-Phase Three-Level Flying Capacitor and Stacked Polyphase Bridge GaN Inverter Systems for Integrated Motor Drives

**Authors:** Gwendolin Rohner, Jonas Huber, Spasoje Mirić, Johann W. Kolar

**Year:** 2024

**Venue:** Electronics

**DOI:** `10.3390/electronics13071259`

**URL:** https://doi.org/10.3390/electronics13071259

**Type:** Journal article

**Target topics:**

- Semiconductor voltage scaling
- Efficiency and loss comparison
- Power density and thermal management
- Integrated modular motor drives

**Potential comparison fields:**

- `rated_power_kw`
- `peak_power_kw`
- `dc_link_voltage_v`
- `cell_voltage_v`
- `number_of_cells`
- `number_of_phases`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`

**Why this paper may be useful:**

Highly targeted comparison of a 7.5 kW integrated drive using an 800 V DC link, series-stacked two-level converters, and 650 V GaN devices; likely one of the strongest sources for paired voltage-rating, cell-count, efficiency, and power-density fields.

**Experimental relevance:**

Appears to combine detailed design analysis with an integrated-drive comparison; experimental validation scope must be checked.

**Expected full-text value:**

Very high for nearly all critical comparison fields.

**Current verification:** `CANDIDATE_METADATA_ONLY`

---

### 9. Holistic Design and Development of a 100-kW SiC-Based Six-Phase Traction Inverter for an Electric Vehicle Application

**Authors:** Wesam Taha, Francisco Juarez-Leon, Mohamed Hefny, Anandajith Jinesh, Matthew Poulton, Berker Bilgin, Ali Emadi

**Year:** 2024

**Venue:** IEEE Transactions on Transportation Electrification

**DOI:** `10.1109/TTE.2023.3313511`

**URL:** https://doi.org/10.1109/TTE.2023.3313511

**Type:** Journal article

**Target topics:**

- Semiconductor voltage scaling
- Power density and thermal management
- Experimental demonstrations

**Potential comparison fields:**

- `rated_power_kw`
- `peak_power_kw`
- `number_of_phases`
- `semiconductor_voltage_rating_v`
- `semiconductor_current_rating_a`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`

**Why this paper may be useful:**

High-value experimental six-phase traction-inverter paper explicitly centered on a 100 kW SiC design, liquid cooling, electrothermal sizing, and compact packaging; likely useful for power, phase count, thermal, efficiency, and power-density records.

**Experimental relevance:**

Strong: prototype inverter reportedly fabricated and experimentally tested.

**Expected full-text value:**

Very high for traction-scale quantitative comparison, although it is not specifically an SPB topology.

**Current verification:** `CANDIDATE_METADATA_ONLY`

---

### 10. Loss Analysis and Mapping of a SiC MOSFET Based Segmented Two-Level Three-Phase Inverter for EV Traction Systems

**Authors:** Emre Gurpinar, Burak Ozpineci

**Year:** 2018

**Venue:** 2018 IEEE Transportation Electrification Conference and Expo (ITEC)

**DOI:** `10.1109/ITEC.2018.8450188`

**URL:** https://doi.org/10.1109/ITEC.2018.8450188

**Type:** Conference paper

**Target topics:**

- Efficiency and loss comparison
- Semiconductor voltage scaling
- Experimental demonstrations

**Potential comparison fields:**

- `rated_power_kw`
- `dc_link_voltage_v`
- `semiconductor_voltage_rating_v`
- `semiconductor_current_rating_a`
- `switching_frequency_khz`
- `efficiency_percent`

**Why this paper may be useful:**

Directly addresses loss mapping of a segmented SiC inverter for EV traction; potentially useful for measured/modelled efficiency, operating-condition, device-rating, and segmented-converter comparisons.

**Experimental relevance:**

Likely includes traction-inverter loss validation; full text required.

**Expected full-text value:**

High for loss and efficiency fields; power density may not be reported.

**Current verification:** `CANDIDATE_METADATA_ONLY`

---

### 11. Efficiency Comparison of 2-Level SiC Inverter and Soft Switching-Snubber SiC Inverter for Electric Motor Drives

**Authors:** Marco di Benedetto, Luca Bigarelli, Alessandro Lidozzi, Luca Solero

**Year:** 2021

**Venue:** Energies

**DOI:** `10.3390/en14061690`

**URL:** https://doi.org/10.3390/en14061690

**Type:** Journal article

**Target topics:**

- Efficiency and loss comparison
- Semiconductor voltage scaling
- Experimental demonstrations

**Potential comparison fields:**

- `rated_power_kw`
- `dc_link_voltage_v`
- `semiconductor_voltage_rating_v`
- `switching_frequency_khz`
- `efficiency_percent`

**Why this paper may be useful:**

Provides a direct two-level SiC inverter efficiency comparison, potentially supplying operating-point and loss data useful as a non-stacked baseline for the review.

**Experimental relevance:**

Likely includes hardware-based motor-drive testing; verify in full text.

**Expected full-text value:**

Moderate to high for efficiency and loss comparison, lower for phase/cell-count fields.

**Current verification:** `CANDIDATE_METADATA_ONLY`

---

### 12. Design and Experimental Validation of a High-Power-Density GaN-Based Inverter Module for Integrated Modular Motor Drives in All-Electric Aircraft Applications

**Authors:** Armin Ebrahimian, Seyed Iman Hosseini Sabzevari, Nathan Weise

**Year:** 2025

**Venue:** IEEE Journal of Emerging and Selected Topics in Power Electronics

**DOI:** `10.1109/JESTPE.2025.3564792`

**URL:** https://doi.org/10.1109/JESTPE.2025.3564792

**Type:** Journal article

**Target topics:**

- Integrated modular motor drives
- Power density and thermal management
- Semiconductor voltage scaling
- Experimental demonstrations

**Potential comparison fields:**

- `rated_power_kw`
- `semiconductor_voltage_rating_v`
- `semiconductor_current_rating_a`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`

**Why this paper may be useful:**

Experimental GaN inverter-module paper for a 250 kW integrated modular drive; likely valuable for module-level scaling, efficiency, semiconductor ratings, and power-density benchmarking.

**Experimental relevance:**

Strong: manufactured module reportedly tested for switching and continuous operation.

**Expected full-text value:**

Very high for high-power modular-drive packaging and efficiency; exact system DC-link and phase-count data require verification.

**Current verification:** `CANDIDATE_METADATA_ONLY`

---

### 13. High Power Density Inverter Utilizing SiC MOSFET and Interstitial Via Hole PCB for Motor Drive System

**Authors:** Authors require confirmation from the full bibliographic record

**Year:** 2020

**Venue:** IEEJ Transactions on Industry Applications

**DOI:** `10.1541/ieejias.140.526`

**URL:** https://doi.org/10.1541/ieejias.140.526

**Type:** Journal article

**Target topics:**

- Power density and thermal management
- Efficiency and loss comparison
- Experimental demonstrations

**Potential comparison fields:**

- `rated_power_kw`
- `semiconductor_voltage_rating_v`
- `semiconductor_current_rating_a`
- `switching_frequency_khz`
- `efficiency_percent`
- `power_density_kw_per_l`

**Why this paper may be useful:**

Experimental 37 kW SiC motor-drive inverter reportedly achieving 81 kW/L; useful for high-power-density, cooling, thermal-rise, and efficiency benchmarking against integrated modular concepts.

**Experimental relevance:**

Strong: rated-load motor-drive performance and temperature rise were reportedly experimentally evaluated.

**Expected full-text value:**

High for power density and thermal fields; topology and phase/cell data may be limited.

**Current verification:** `CANDIDATE_METADATA_ONLY`

---

## Unresolved Literature Gaps

- Exact semiconductor voltage/current ratings, switching frequencies, measured efficiencies, and power densities for most candidates require full-text extraction.
- Some conference candidates may report simulations or design studies rather than measured hardware results.
- Author metadata for two candidates was not fully confirmed from the available bibliographic records and should be resolved before database ingestion.
- Several high-value traction-inverter baselines are not stacked-polyphase architectures; they are included to fill the review’s critical quantitative efficiency, power-density, semiconductor, and thermal-comparison gaps.
