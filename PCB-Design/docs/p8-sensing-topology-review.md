# Independent device sensing versus compactness

Update: the user has now prioritized minimum loop inductance and investigation of smaller sensing methods. The CWTUM geometry below is retained as rejected-option evidence, not the active layout requirement. See p8-smaller-sensing-selection.md.

Review 23 September 2026: the existing board cannot acquire valid individual-current sensing simply by drilling beside the FETs. A winding links all signed current crossings through its aperture, including buried planes. Continuous adjacent return copper can cancel the selected drain-current signal.

A candidate for further layout work is two mirrored power cells with individual drain necks leaving opposite edges of a common central spreader. Put the two coil planes outside those edges, predominantly below the PCB. In each aperture, only its individual drain conductor may cross. Route the common AC feed, DC-minus return, gate returns and other copper outside the aperture. That necessarily changes the field cancellation and complete commutation loop. No numerical loop inductance is released for this arrangement.

For the circular CWTUM installation screened in p8_coil_geometry_screen.py, mirrored below the board, reserve approximately 24 mm transverse space per sensing location, approximately 24 mm below-board height, and 2.7 mm above-board winding envelope. These are winding-only study envelopes, not released dimensions. The calculated slots span roughly 4.77 to 10.12 mm from each coil centre on either side across the circumference tolerance; installation clearance, closure and cable are not included. A different validated noncircular routing could change these requirements.

The new 64 x 42 mm P8 placement study establishes a compact unsensed comparison, not a demonstrated fit for these coils. It deliberately contains no sensing holes or raised links. A choice between retaining the selected coil with additional space/inductance and investigating a smaller sensing method is pending with the user. Preserve the compact comparison while that choice is open.
