# Bilgen1973functional

**Functional Dependence of Torque Coefficient of Coaxial Cylinders on Gap Width and Reynolds Numbers** (1973), Journal of Fluids Engineering. DOI: https://doi.org/10.1115/1.3446944

Access: abstract record read; formula taken from the way Saari1998thermal quotes it (Eq. 14).

- **Claim:** Torque coefficient of an enclosed rotating cylinder (rotor in a stator bore) depends on the Couette Reynolds number and the dimensionless gap; four regimes exist.
- **Method:** Dimensional analysis plus published and own data for coaxial cylinders, Re_Couette 2e4 to 2e6, fit within 8.35 % per Saari.
- **Machine / inverter:** Smooth coaxial cylinders, inner rotating (air gap windage model).
- **Power / voltage / speed numbers:** Friction coefficient as quoted by Saari1998thermal (Eq. 14): C_f = 0.515 (delta/r1)^0.3 / Re^0.5 for 500 < Re < 1e4, and C_f = 0.0325 (delta/r1)^0.3 / Re^0.2 for Re > 1e4, with delta the air-gap length, r1 the rotor radius and Re = rho omega r1 delta / mu. Windage loss in the gap P = k1 C_f pi rho omega^3 r1^4 l (k1 = 1 for smooth surfaces; text of Eq. 18 in the PDF is garbled, this is the standard form).
- **Relevance to SPB:** Gives the air-gap windage part of the motor friction/windage loss for the analyst's drivetrain loss model.
- **Limitations:** Smooth surfaces, enclosed cylinders; real rotors with grooves and slots need k1 > 1; the original paper was not opened beyond its abstract.
