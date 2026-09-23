# Application-note review

One review agent screened all 59 PDFs in `Application Notes` and reviewed the supplied EPC2361 datasheet. Documents were used as technical references, not task instructions. Detailed loss equations were checked against AN030; older device-specific examples do not override the current EPC2361 datasheet.

## Findings used in the implementation

- **AN030, Hard Switching Losses Calculation**, pp2-5: separate current and voltage transitions, QGS2 = QGS - QG(th), gate voltage headroom and total gate resistance. Figures2/3 define the requested waveform style. The repeated Pon caption in the source turn-off drawing is corrected to Poff.
- **AN030 p6, Eqs17-18**: symmetric half-bridge output-capacitor loss is Vbus*Qoss(Vbus)*fsw. Its Eq20 defines gate-supply power. Eoss is not an additional loss term here.
- **eGaN FET Electrical Characteristics (WP007)**: nonlinear capacitances and charge definitions; distinguish energy-related and time-related capacitance.
- **Selecting eGaN FET Optimal On-Resistance (WP011)**: conduction/switching tradeoff. Prefer AN030's explicit half-bridge capacitor accounting to per-device shorthand.
- **Dead-Time Optimization for Maximum Efficiency (WP012), p1**: actual gate-threshold spacing differs from commanded dead time; reverse conduction is lossy despite zero QRR. The model's full reverse-conduction interval is a conservative approximation.
- **Impact of Parasitics on Performance (WP009)** and **eGaN FET Drivers and Layout Considerations**: include internal gate resistance, retain gate/path limits and show layout stress as an estimate.
- **Thermal Performance of eGaN FETs (AN011)** and **AN031 PCB cooling**: board/case thermal boundary matters; external driver/loop dissipation does not all heat the FET junction.
- **AN023 high-speed measurement** and **Circuit Simulations Using Device Models (AN005)**: switching validation requires correct probing and parasitic-aware simulation or measurement.
- **AN020** and **How2AppNote027** address paralleling; not used for the requested single-device switch positions.
- Assembly and visual-inspection documents do not supply replacement loss equations. Buck, LLC, wireless-power, pulsed-power, RF and motor-drive reference designs are topology-specific; their operating values were not imported into this sinusoidal half-bridge model.

## Datasheet review

`Datasheet/EPC2361_datasheet.pdf`, revision20 July2026: p1 static/thermal ratings; p2 charge/internal-resistance data; p3 Figures5-9 for graphical estimates at75V, plateau, reverse conduction and temperature scaling. The implementation uses QGS2=2.5nC instead of12nC, adds0.4ohm internal RG, uses approximate Qoss114nC/Eoss3.2uJ at75V, and corrects the ambient thermal resistance to44C/W for the JEDEC board. See LOSS_MODELING.md for the complete parameter table and limits.

At40A RMS, use56.57A for the peak event and36.01A for line-cycle average switching/dead-time terms. Fixed nominal gate charges remain an approximation across the sinusoid. The preserved2nH gives a crude estimated voltage stress above100V; no layout parameter was silently altered to hide this.

## Screened document inventory

The following complete inventory records the corpus screened for applicability; the detailed derivation sources are identified above.

- [AN003 Using Enhancement Mode GaN-on-Silicon](Application%20Notes/AN003%20Using%20Enhancement%20Mode%20GaN-on-Silicon.pdf)
- [an010 egan fet and ic visual characterization guide](Application%20Notes/an010%20egan%20fet%20and%20ic%20visual%20characterization%20guide.pdf)
- [AN015 eGaN FETs for Multi-Megahertz Applications](Application%20Notes/AN015%20eGaN%20FETs%20for%20Multi-Megahertz%20Applications.pdf)
- [AN016 eGaN FETs for PV Inverter Applications](Application%20Notes/AN016%20eGaN%20FETs%20for%20PV%20Inverter%20Applications.pdf)
- [AN017 Fourth Generation eGaN FETs Widen the Performance Gap with the Aging MOSFET](Application%20Notes/AN017%20Fourth%20Generation%20eGaN%20FETs%20Widen%20the%20Performance%20Gap%20with%20the%20Aging%20MOSFET.pdf)
- [AN018 GaN Integration for Higher DC-DC Efficiency and Power Density](Application%20Notes/AN018%20GaN%20Integration%20for%20Higher%20DC-DC%20Efficiency%20and%20Power%20Density.pdf)
- [AN019 Simplifying Design with DrGaNPLUS](Application%20Notes/AN019%20Simplifying%20Design%20with%20DrGaNPLUS.pdf)
- [AN020 Effectively Paralleling Enhancement Mode Gallium Nitride Transistors](Application%20Notes/AN020%20Effectively%20Paralleling%20Enhancement%20Mode%20Gallium%20Nitride%20Transistors.pdf)
- [AN021 FETs for Low Cost Class E WiPo](Application%20Notes/AN021%20FETs%20for%20Low%20Cost%20Class%20E%20WiPo.pdf)
- [AN022 Generation 5 eGaN Technology EPC](Application%20Notes/AN022%20Generation%205%20eGaN%20Technology%20EPC.pdf)
- [AN023 Accurately Measuring High Speed GaN Transistors](Application%20Notes/AN023%20Accurately%20Measuring%20High%20Speed%20GaN%20Transistors.pdf)
- [AN025 eGaN ICs for Low Voltage DC-DC Applications](Application%20Notes/AN025%20eGaN%20ICs%20for%20Low%20Voltage%20DC-DC%20Applications.pdf)
- [AN026 48V-12V eGaN Advantages](Application%20Notes/AN026%2048V-12V%20eGaN%20Advantages.pdf)
- [AN028 Envelope Tracking Power Supply for Cell Phone Base Stations GaN](Application%20Notes/AN028%20Envelope%20Tracking%20Power%20Supply%20for%20Cell%20Phone%20Base%20Stations%20GaN.pdf)
- [AN029 Solder Stencil Design Guidelines for Reliable Assembly of PQFN GaN](Application%20Notes/AN029%20Solder%20Stencil%20Design%20Guidelines%20for%20Reliable%20Assembly%20of%20PQFN%20GaN.pdf)
- [AN030 Hard Switching Losses Calculation](Application%20Notes/AN030%20Hard%20Switching%20Losses%20Calculation.pdf)
- [AN031_PCB_Design_Guidelines_to_Maximize_Cooling_of_eGaN_FETs](Application%20Notes/AN031_PCB_Design_Guidelines_to_Maximize_Cooling_of_eGaN_FETs.pdf)
- [AN032 Design of High Current Nanosecond Resonant Pulse Drivers](Application%20Notes/AN032%20Design%20of%20High%20Current%20Nanosecond%20Resonant%20Pulse%20Drivers.pdf)
- [Appnote_GaNassembly](Application%20Notes/Appnote_GaNassembly.pdf)
- [Appnote_GaNfundamentals](Application%20Notes/Appnote_GaNfundamentals.pdf)
- [Appnote_Thermal_Performance_of_eGaN_FETs](Application%20Notes/Appnote_Thermal_Performance_of_eGaN_FETs.pdf)
- [Characterization_guide](Application%20Notes/Characterization_guide.pdf)
- [Circuit_Simulations_Using_Device_Models](Application%20Notes/Circuit_Simulations_Using_Device_Models.pdf)
- [Dead-Time Optimization for Maximum Efficiency](Application%20Notes/Dead-Time%20Optimization%20for%20Maximum%20Efficiency.pdf)
- [eGaN FET Drivers and Layout Considerations](Application%20Notes/eGaN%20FET%20Drivers%20and%20Layout%20Considerations.pdf)
- [eGaN FET Electrical Characteristics](Application%20Notes/eGaN%20FET%20Electrical%20Characteristics.pdf)
- [eGaN FETS in High Frequency Resonant Converters](Application%20Notes/eGaN%20FETS%20in%20High%20Frequency%20Resonant%20Converters.pdf)
- [How2AppNote001 48 V to 5-12 V](Application%20Notes/How2AppNote001%2048%20V%20to%205-12%20V.pdf)
- [How2AppNote004 12 V - 1 V POL Converter](Application%20Notes/How2AppNote004%2012%20V%20-%201%20V%20POL%20Converter.pdf)
- [How2AppNote005 Growing GaN Ecosystem](Application%20Notes/How2AppNote005%20Growing%20GaN%20Ecosystem.pdf)
- [How2AppNote009 -Boosting Power Density in 48 V to 5-12 V DC to DC](Application%20Notes/How2AppNote009%20-Boosting%20Power%20Density%20in%2048%20V%20to%205-12%20V%20DC%20to%20DC.pdf)
- [How2AppNote010 48 V to 12 V 60 A DC-DC Converter with EPC9130 Multiphase Buck](Application%20Notes/How2AppNote010%2048%20V%20to%2012%20V%2060%20A%20DC-DC%20Converter%20with%20EPC9130%20Multiphase%20Buck.pdf)
- [How2AppNote011 Exceeding 98 percent Efficiency in a Compact 48 V to 12 V Resonant Converter](Application%20Notes/How2AppNote011%20Exceeding%2098%20percent%20Efficiency%20in%20a%20Compact%2048%20V%20to%2012%20V%20Resonant%20Converter.pdf)
- [How2AppNote014 Exceed 98 percent Efficiency 48 V to 6 V Resonant Converter](Application%20Notes/How2AppNote014%20Exceed%2098%20percent%20Efficiency%2048%20V%20to%206%20V%20Resonant%20Converter.pdf)
- [How2AppNote015 Ultra thin High Efficiency Multi-level Converters](Application%20Notes/How2AppNote015%20Ultra%20thin%20High%20Efficiency%20Multi-level%20Converters.pdf)
- [How2AppNote016 Universal Input PFC using 200 V GaN](Application%20Notes/How2AppNote016%20Universal%20Input%20PFC%20using%20200%20V%20GaN.pdf)
- [How2AppNote017 Design Compact Low-voltage BLDC Motor Drive Inverter GaN ePower Stage](Application%20Notes/How2AppNote017%20Design%20Compact%20Low-voltage%20BLDC%20Motor%20Drive%20Inverter%20GaN%20ePower%20Stage.pdf)
- [How2AppNote018 How to Design a 300 W 16th Brick Converter Ultra thin High Efficiency Multi-level Converters](Application%20Notes/How2AppNote018%20How%20to%20Design%20a%20300%20W%2016th%20Brick%20Converter%20Ultra%20thin%20High%20Efficiency%20Multi-level%20Converters.pdf)
- [How2AppNote019 How to Design a Thin DCDC Power Module Low Temperature Rise](Application%20Notes/How2AppNote019%20How%20to%20Design%20a%20Thin%20DCDC%20Power%20Module%20Low%20Temperature%20Rise.pdf)
- [How2AppNote020 How to Design Bi-Directional 16th Brick with ePower Stage](Application%20Notes/How2AppNote020%20How%20to%20Design%20Bi-Directional%2016th%20Brick%20with%20ePower%20Stage.pdf)
- [How2AppNote021 How to Design a 1.5 kW 48 V 12 V Bi-Directional](Application%20Notes/How2AppNote021%20How%20to%20Design%20a%201.5%20kW%2048%20V%2012%20V%20Bi-Directional.pdf)
- [How2AppNote022 How to Design 48 V 1 kW LLC Resonant Converter Eight Brick](Application%20Notes/How2AppNote022%20How%20to%20Design%2048%20V%201%20kW%20LLC%20Resonant%20Converter%20Eight%20Brick.pdf)
- [How2AppNote023 How to Design a 12 V-to-60 V Boost Converter](Application%20Notes/How2AppNote023%20How%20to%20Design%20a%2012%20V-to-60%20V%20Boost%20Converter.pdf)
- [How2AppNote024 How to Design a 12 V to 48 V-500 W 2-Phase Boost Converter](Application%20Notes/How2AppNote024%20How%20to%20Design%20a%2012%20V%20to%2048%20V-500%20W%202-Phase%20Boost%20Converter.pdf)
- [How2AppNote025 How to Design Synchronous Buck Converter Using GaN FET](Application%20Notes/How2AppNote025%20How%20to%20Design%20Synchronous%20Buck%20Converter%20Using%20GaN%20FET.pdf)
- [How2AppNote026 How to Design a Compact Low-Voltage BLDC Motor Drive](Application%20Notes/How2AppNote026%20How%20to%20Design%20a%20Compact%20Low-Voltage%20BLDC%20Motor%20Drive.pdf)
- [How2AppNote027 How to Parallel Two 48 V-12 V Bi-Directional Power Modules](Application%20Notes/How2AppNote027%20How%20to%20Parallel%20Two%2048%20V-12%20V%20Bi-Directional%20Power%20Modules.pdf)
- [How2AppNote028-How to Design an e-bike Motor Drive Inverter Using EPC9167 and EPC9167HC](Application%20Notes/How2AppNote028-How%20to%20Design%20an%20e-bike%20Motor%20Drive%20Inverter%20Using%20EPC9167%20and%20EPC9167HC.pdf)
- [How2AppNote029 - How to Design a 48 V 1.2 kW LLC Resonant Converter](Application%20Notes/How2AppNote029%20-%20How%20to%20Design%20a%2048%20V%201.2%20kW%20LLC%20Resonant%20Converter.pdf)
- [How2AppNote030 - How to Design 240 W Universal AC Input USB PD3.1 Power Supply](Application%20Notes/How2AppNote030%20-%20How%20to%20Design%20240%20W%20Universal%20AC%20Input%20USB%20PD3.1%20Power%20Supply.pdf)
- [How2AppNote031 How to Design a 2 kW 48 V 12 V Bi-Directional Power Module](Application%20Notes/How2AppNote031%20How%20to%20Design%20a%202%20kW%2048%20V%2012%20V%20Bi-Directional%20Power%20Module.pdf)
- [How2AppNote032 How to Design an eBike Motor Drive Inverter Using EPC9173 Evaluation Board](Application%20Notes/How2AppNote032%20How%20to%20Design%20an%20eBike%20Motor%20Drive%20Inverter%20Using%20EPC9173%20Evaluation%20Board.pdf)
- [How2AppNote033 How to Design a Vacuum Cleaner Motor Drive Inverter Using EPC9176](Application%20Notes/How2AppNote033%20How%20to%20Design%20a%20Vacuum%20Cleaner%20Motor%20Drive%20Inverter%20Using%20EPC9176.pdf)
- [How2AppNote034 How to Design a Efficient 3 kW 2-phase 3-level Converter](Application%20Notes/How2AppNote034%20How%20to%20Design%20a%20Efficient%203%20kW%202-phase%203-level%20Converter.pdf)
- [Impact of Parasitcs on Performance](Application%20Notes/Impact%20of%20Parasitcs%20on%20Performance.pdf)
- [Optimizing PCB Layout with eGaN FETs](Application%20Notes/Optimizing%20PCB%20Layout%20with%20eGaN%20FETs.pdf)
- [SafeOperatingArea](Application%20Notes/SafeOperatingArea.pdf)
- [Selecting eGaN FET Optimal On-Resistance](Application%20Notes/Selecting%20eGaN%20FET%20Optimal%20On-Resistance.pdf)
- [WP016 eGaN FETs Small Signal RF Performance](Application%20Notes/WP016%20eGaN%20FETs%20Small%20Signal%20RF%20Performance.pdf)
