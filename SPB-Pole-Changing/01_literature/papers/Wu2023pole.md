# Wu2023pole

**Pole-Transition Control of Variable-Pole Machines Using Harmonic-Plane Decomposition** (2023), IEEE Transactions on Industrial Electronics. DOI: https://doi.org/10.1109/tie.2022.3231328

Access: abstract + full text read (KTH DiVA postprint).

- **Claim:** Harmonic-plane decomposition (HPD) generalises VSD so loaded pole transitions of variable phase-pole machines remain continuous; controlled loaded pole change on a WICSC machine with two transition strategies keeps torque.
- **Method:** HPD-based indirect rotor field-oriented control; experiment.
- **Machine / inverter:** WICSC IM (independently controlled stator coils), KTH.
- **Power / voltage / speed numbers:** No numbers in abstract.
- **Full-text addition:** Experiment: WICSC machine from a 15 kW ABB 3GAA161420-BDG induction motor (Qs = 36, Qr = 28, 400 V, 2934 rpm, 48.8 N m, cos phi 0.9), each of the 36 slots fed by its own inverter leg (36-leg 2-level inverter, DC bus 107 V, 8 kHz carrier PWM, minimum windings with one single isolated neutral point). Loaded 4.5 N m transition from [m = 9 phases, p = 1] to [m = 4.5, p = 4] with pre-/de-magnetisation times (t_preDeMag = 0.69 tau_R = 0.528 s, t_preMag = 2 tau_R = 0.211 s); the premagnetised transition shortens the electrical transient by 100 ms and the speed settling time by 64 ms versus a hard switch.
- **Relevance to SPB:** Control theory for the isolated-coil-group pole change that SPB would run.
- **Limitations:** Lab scale.
- **SPB note (from full text):** Machine with an isolated neutral and a leg per coil group is exactly the SPB electrical structure; shows a loaded 4.5 N m pole change with FOC and rotor-flux hand-over.
