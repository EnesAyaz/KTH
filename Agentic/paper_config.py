# =========================================================
# PAPER INFORMATION
# =========================================================

PAPER_TITLE = (
    "Stacked Polyphase Bridge Converters for "
    "High-Power Electric Traction Drives: A Review"
)


AUTHOR_NAME = (
    "Enes Ayaz"
)


# =========================================================
# REVIEW PAPER SECTIONS
# =========================================================

SECTIONS = [

    {
        "number": 1,

        "title":
            "Introduction",

        "evidence_section":
            "Introduction",

        "filename":
            "01_introduction.tex",

        "target_words":
            800,

        "objectives": [
            "Motivate high-voltage and high-power traction drives.",
            "Introduce limitations of conventional traction inverter scaling.",
            "Introduce stacked polyphase bridge converters.",
            "Define the purpose and scope of the review.",
            "Summarize the organization of the paper.",
        ],
    },

    {
        "number": 2,

        "title":
            "Background and Taxonomy",

        "evidence_section":
            "Background and Taxonomy",

        "filename":
            "02_background_taxonomy.tex",

        "target_words":
            900,

        "objectives": [
            "Define stacked polyphase bridge converters.",
            "Distinguish them from other modular converter architectures.",
            "Compare conventional two-level, multilevel, multiphase, open-end winding, and modular alternatives.",
            "Establish terminology used throughout the review.",
        ],
    },

    {
        "number": 3,

        "title":
            "Stacked Polyphase Bridge Architecture",

        "evidence_section":
            "Converter Architecture",

        "filename":
            "03_converter_architecture.tex",

        "target_words":
            1000,

        "objectives": [
            "Explain the basic operating principle.",
            "Explain DC-side series stacking.",
            "Explain the relationship between bridge cells and machine winding groups.",
            "Discuss voltage and current scaling.",
            "Discuss architectural benefits and limitations.",
        ],
    },

    {
        "number": 4,

        "title":
            "Multiphase Electric Machine Requirements",

        "evidence_section":
            "Multiphase Electric Machines",

        "filename":
            "04_multiphase_machines.tex",

        "target_words":
            1000,

        "objectives": [
            "Explain compatible machine winding structures.",
            "Discuss isolated winding groups.",
            "Discuss phase number and machine complexity.",
            "Discuss harmonic subspaces.",
            "Discuss fault-tolerant operation.",
        ],
    },

    {
        "number": 5,

        "title":
            "Semiconductor Technology and Voltage Scaling",

        "evidence_section":
            "Semiconductor Technology",

        "filename":
            "05_semiconductors.tex",

        "target_words":
            1100,

        "objectives": [
            "Compare Si, SiC, and GaN possibilities.",
            "Explain semiconductor voltage scaling through stacking.",
            "Discuss low-voltage versus high-voltage device approaches.",
            "Discuss conduction and switching tradeoffs.",
            "Discuss device-count implications.",
        ],
    },

    {
        "number": 6,

        "title":
            "Modulation, Control, and Cell Balancing",

        "evidence_section":
            "Modulation and Control",

        "filename":
            "06_modulation_control.tex",

        "target_words":
            1100,

        "objectives": [
            "Review suitable modulation methods.",
            "Discuss synchronization among cells.",
            "Discuss DC-side balancing.",
            "Discuss control complexity.",
            "Discuss dynamic traction operation.",
        ],
    },

    {
        "number": 7,

        "title":
            "Common-Mode Voltage and Electromagnetic Compatibility",

        "evidence_section":
            "Common-Mode Voltage and EMI",

        "filename":
            "07_common_mode_emi.tex",

        "target_words":
            800,

        "objectives": [
            "Discuss common-mode voltage generation.",
            "Discuss bearing currents and insulation stress.",
            "Discuss EMI implications.",
            "Review mitigation possibilities.",
        ],
    },

    {
        "number": 8,

        "title":
            "Fault Tolerance and Reliability",

        "evidence_section":
            "Fault Tolerance",

        "filename":
            "08_fault_reliability.tex",

        "target_words":
            1000,

        "objectives": [
            "Classify important converter and machine faults.",
            "Discuss cell isolation and reconfiguration.",
            "Discuss post-fault torque capability.",
            "Discuss reliability implications of increased component count.",
            "Discuss traction safety considerations.",
        ],
    },

    {
        "number": 9,

        "title":
            "Efficiency, Power Density, and Thermal Management",

        "evidence_section":
            "Losses and Efficiency",

        "filename":
            "09_efficiency_thermal.tex",

        "target_words":
            1200,

        "objectives": [
            "Compare converter loss mechanisms.",
            "Discuss machine harmonic losses.",
            "Discuss efficiency implications of stacking.",
            "Discuss power-density definitions.",
            "Discuss thermal-management requirements.",
        ],
    },

    {
        "number": 10,

        "title":
            "Integrated Modular Motor Drives",

        "evidence_section":
            "Integrated Motor Drives",

        "filename":
            "10_integrated_drives.tex",

        "target_words":
            900,

        "objectives": [
            "Introduce integrated modular motor-drive concepts.",
            "Discuss inverter-machine integration.",
            "Discuss interconnect and packaging benefits.",
            "Discuss thermal and serviceability challenges.",
        ],
    },

    {
        "number": 11,

        "title":
            "Experimental Demonstrations and Technology Maturity",

        "evidence_section":
            "Experimental Validation",

        "filename":
            "11_experimental_validation.tex",

        "target_words":
            1000,

        "objectives": [
            "Classify available experimental demonstrations.",
            "Compare scale, voltage, power, and operating conditions.",
            "Assess which claimed benefits have experimental support.",
            "Discuss technology readiness.",
        ],
    },

    {
        "number": 12,

        "title":
            "Systematic Comparative Assessment",

        "evidence_section":
            "System-Level Comparison",

        "filename":
            "12_system_comparison.tex",

        "target_words":
            1200,

        "objectives": [
            "Synthesize the literature across converter architectures.",
            "Compare semiconductor requirements.",
            "Compare machine complexity.",
            "Compare efficiency and power density.",
            "Compare reliability and fault tolerance.",
            "Discuss application dependence.",
        ],
    },

    {
        "number": 13,

        "title":
            "Research Gaps",

        "evidence_section":
            "Research Gaps",

        "filename":
            "13_research_gaps.tex",

        "target_words":
            900,

        "objectives": [
            "Identify gaps that are directly supported by the reviewed evidence.",
            "Identify missing full-power validation.",
            "Discuss balancing, thermal, reliability, and insulation gaps.",
            "Discuss semiconductor maturity.",
            "Avoid inventing research gaps unsupported by the review.",
        ],
    },

    {
        "number": 14,

        "title":
            "Future Research Directions",

        "evidence_section":
            "Future Research Directions",

        "filename":
            "14_future_research.tex",

        "target_words":
            800,

        "objectives": [
            "Propose evidence-based research directions.",
            "Discuss converter-machine-thermal co-design.",
            "Discuss modular cell concepts.",
            "Discuss advanced control and diagnostics.",
            "Discuss vehicle-level validation.",
        ],
    },

    {
        "number": 15,

        "title":
            "Conclusion",

        "evidence_section":
            "Conclusion",

        "filename":
            "15_conclusion.tex",

        "target_words":
            600,

        "objectives": [
            "Answer the central review question.",
            "Summarize demonstrated advantages.",
            "Summarize important limitations.",
            "Identify the most promising application conditions.",
            "Avoid claiming universal superiority.",
        ],
    },
]