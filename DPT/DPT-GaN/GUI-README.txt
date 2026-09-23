EPC LTspice parameter editor

Double-click Launch-GUI.cmd (requires Python with Tkinter, already checked on this PC).
Change values in either tab, then choose Save copy or Save and open in LTspice.
The latter uses the Windows .asc file association. Run the simulation in LTspice.
The original source schematic is protected from overwriting.
When saving elsewhere, the symbol and library are copied alongside the output.
The library include is changed to a relative path in the generated copy.

The existing circuit topology, EPC2361 models, measurements, initial conditions,
and 0.6 ms transient command are preserved. Timing validation follows the existing
low-side pulse expression and the last-10-cycles transient saving window.
This is an editor for this example circuit and compatible copies, not an arbitrary
LTspice schematic editor. It does not run or plot simulations inside Python.

Existing model note: Example-EPC.log reports an unknown C2 node in the initial
condition. The editor leaves this original directive unchanged.

Verification: defaults parsed, parameter and component changes checked, circuit
connections preserved, original encoding preserved, invalid timing rejected,
and Tkinter window constructed successfully. Simulation results were not verified.
