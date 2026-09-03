SEVERITY: MAJOR  
LOCATION: Opening paragraph  
PROBLEM: The statement that each submodule “may require independent power regulation” and that the architecture is distinguished from a conventional traction inverter is not directly supported by the supplied evidence.  
WHY IT MATTERS: The cited evidence establishes a particular control structure, but not the broader architectural comparison or its necessity.  
RECOMMENDED ACTION: Qualify the statement or provide supporting literature. ADDITIONAL LITERATURE REQUIRED.

SEVERITY: MAJOR  
LOCATION: Paragraph 2  
PROBLEM: “Standard field-oriented current control in each submodule” is supported, but the claims that the separation is suitable for traction applications and that torque control can remain conceptually conventional are interpretive extensions.  
WHY IT MATTERS: The evidence does not demonstrate traction-level performance, bandwidth separation, or preservation of torque response.  
RECOMMENDED ACTION: Distinguish the reported method from the authors’ interpretation and retain the stated limitations.

SEVERITY: MAJOR  
LOCATION: Paragraph 3  
PROBLEM: The assertion that balancing power is superimposed “without producing unacceptable current distortion or torque ripple” is posed as a design requirement, but no evidence quantifies or demonstrates compliance.  
WHY IT MATTERS: This is a central performance claim for the control method.  
RECOMMENDED ACTION: State explicitly that distortion and torque-ripple performance are unverified. ADDITIONAL LITERATURE REQUIRED.

SEVERITY: MAJOR  
LOCATION: Paragraph 4  
PROBLEM: The citation supports the carrier arrangement and generally supports harmonic cancellation and reduced capacitance, but the manuscript does not specify which harmonics, under what operating conditions, or whether capacitance reduction was experimentally demonstrated.  
WHY IT MATTERS: Harmonic cancellation depends on modulation index, switching frequency, cell matching, timing accuracy, and load conditions.  
RECOMMENDED ACTION: Report the applicable conditions and distinguish theoretical behavior from measured results.

SEVERITY: MAJOR  
LOCATION: Paragraph 5  
PROBLEM: The discussion of communication delay, clock mismatch, sampling asynchronism, and switching-frequency variation is reasonable but unsupported by the supplied evidence.  
WHY IT MATTERS: These are important limitations, but they should not be presented as literature-established findings when only the nominal carrier relationship is documented.  
RECOMMENDED ACTION: Identify these explicitly as open issues and add evidence. ADDITIONAL LITERATURE REQUIRED.

SEVERITY: MAJOR  
LOCATION: Paragraph 6  
PROBLEM: The manuscript claims that carrier, control, and measurement synchronization are all required, but Jin2017 is verified only for coordinated carriers and submodule-level control; measurement synchronization and comparative centralized/distributed implementations are unsupported.  
WHY IT MATTERS: The synchronization requirements may differ by implementation and should not be generalized from one reported method.  
RECOMMENDED ACTION: Limit the claim to the demonstrated architecture and provide additional literature. ADDITIONAL LITERATURE REQUIRED.

SEVERITY: MAJOR  
LOCATION: Paragraph 7  
PROBLEM: The claim that computational burden and control bandwidth scale with \(N\) is plausible but not demonstrated.  
WHY IT MATTERS: The scaling depends on controller architecture, sampling, communication, and hardware partitioning; it cannot be inferred solely from the number of states.  
RECOMMENDED ACTION: Present this as an unverified design concern and provide quantitative evidence if retained. ADDITIONAL LITERATURE REQUIRED.

SEVERITY: MAJOR  
LOCATION: Paragraph 8  
PROBLEM: The section discusses acceleration, regeneration, low-speed operation, voltage margin, and complete traction cycles, but the supplied evidence contains no operating-condition data or dynamic validation.  
WHY IT MATTERS: The manuscript risks implying traction applicability from a conceptual control structure.  
RECOMMENDED ACTION: Clearly separate proposed applicability from demonstrated results and report test conditions where available. ADDITIONAL LITERATURE REQUIRED.

SEVERITY: MAJOR  
LOCATION: Paragraph 9  
PROBLEM: Claims concerning switching losses, rms-current distribution, thermal loading, and the need for temperature-balancing constraints are unsupported by the supplied evidence.  
WHY IT MATTERS: These are substantive technical conclusions, not merely qualitative consequences; balancing capacitor voltage does not automatically establish unequal thermal stress.  
RECOMMENDED ACTION: Either support these claims with loss/thermal analysis or qualify them as potential secondary effects. ADDITIONAL LITERATURE REQUIRED.

SEVERITY: MAJOR  
LOCATION: Overall section  
PROBLEM: The section relies almost entirely on one source and does not synthesize competing modulation, balancing, synchronization, or distributed-control approaches.  
WHY IT MATTERS: A review paper should establish the state of the field, not only describe one architecture.  
RECOMMENDED ACTION: Add comparative literature on balancing methods, carrier-based and space-vector modulation, centralized versus distributed control, fault-tolerant synchronization, and dynamic validation. ADDITIONAL LITERATURE REQUIRED.

SEVERITY: MINOR  
LOCATION: Paragraph 1 and conclusion  
PROBLEM: “Established vector-control principles” and “improved dc-side harmonic performance” are broad formulations without quantitative comparison.  
WHY IT MATTERS: They may overstate generality and performance relative to alternative methods.  
RECOMMENDED ACTION: Qualify the language and include comparative metrics only when operating conditions are specified.

SEVERITY: MINOR  
LOCATION: Overall section  
PROBLEM: Several paragraphs repeat that the evidence does not establish bandwidth, robustness, scalability, or transient performance.  
WHY IT MATTERS: Repetition weakens synthesis and organization.  
RECOMMENDED ACTION: Consolidate limitations into a structured subsection or summary table.

OVERALL ASSESSMENT: The section accurately reports the two directly verified contributions of Jin2017: hierarchical active-power balancing with field-oriented control, and phase-shifted carrier modulation. However, many traction-performance, synchronization, scalability, thermal, and dynamic claims extend beyond the supplied evidence. The review also lacks comparative literature and quantitative operating conditions.

MAJOR REVISION